# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import annotations

import asyncio
import contextlib
import copy
import os
import pathlib
import time
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Generator

import filelock
import jwt
import platformdirs
import pydantic
import strictyaml

import atrclient.models as models
import atrclient.show as show
import atrclient.web as web

YAML_DEFAULTS: dict[str, Any] = {"asf": {}, "atr": {}, "tokens": {}}
YAML_SCHEMA: strictyaml.Map = strictyaml.Map(
    {
        strictyaml.Optional("atr"): strictyaml.Map({strictyaml.Optional("host"): strictyaml.Str()}),
        strictyaml.Optional("asf"): strictyaml.Map({strictyaml.Optional("uid"): strictyaml.Str()}),
        strictyaml.Optional("tokens"): strictyaml.Map(
            {
                strictyaml.Optional("pat"): strictyaml.Str(),
                strictyaml.Optional("jwt"): strictyaml.Str(),
            }
        ),
    }
)


def drop(config: dict[str, Any], parts: list[str]) -> None:
    walk(config, parts, "drop")


def get(config: dict[str, Any], parts: list[str]) -> Any | None:
    return walk(config, parts, "get")[1]


def host_get() -> tuple[str, bool]:
    with lock() as config:
        host = config.get("atr", {}).get("host", "release-test.apache.org")
    local_domains = ["localhost.apache.org", "127.0.0.1"]
    domain = host.split(":")[0]
    verify_ssl = domain not in local_domains
    return host, verify_ssl


def jwt_get() -> str | None:
    with lock() as config:
        jwt_value = get(config, ["tokens", "jwt"])
    return jwt_value


def jwt_payload() -> tuple[str | None, dict[str, Any]]:
    jwt_value = jwt_get()
    if jwt_value is None:
        return None, {}
    if jwt_value == "dummy_jwt_token":
        # TODO: Use a better test JWT
        return jwt_value, {"exp": time.time() + 90 * 60, "sub": "test_asf_uid"}

    try:
        payload = jwt.decode(jwt_value, options={"verify_signature": False})
    except jwt.PyJWTError as e:
        show.error_and_exit(f"Failed to decode JWT: {e}")
    if not isinstance(payload, dict):
        show.error_and_exit("Invalid JWT payload.")
    return jwt_value, payload


def jwt_refresh(asf_uid: str | None = None) -> str:
    with lock() as config:
        pat_value = get(config, ["tokens", "pat"])
        if asf_uid is None:
            asf_uid = config.get("asf", {}).get("uid")

    if pat_value is None:
        show.error_and_exit("No Personal Access Token stored.")
    if asf_uid is None:
        show.error_and_exit("No ASF UID provided and asf.uid not configured.")

    host, verify_ssl = host_get()
    url = f"https://{host}/api/jwt/create"
    args = models.api.JwtCreateArgs(asfuid=asf_uid, pat=pat_value)
    response = asyncio.run(web.post(url, args, jwt_token=None, verify_ssl=verify_ssl))
    try:
        jwt_results = models.api.validate_jwt_create(response)
    except (pydantic.ValidationError, models.api.ResultsTypeError) as e:
        show.error_and_exit(f"Unexpected API response: {response}\n{e}")

    with lock(write_to_disk=True) as config:
        set_value(config, ["tokens", "jwt"], jwt_results.jwt)

    return jwt_results.jwt


def jwt_usable() -> str:
    with lock() as config:
        config_asf_uid = get(config, ["asf", "uid"])

    jwt_value, payload = jwt_payload()
    if jwt_value is None:
        if config_asf_uid is None:
            show.error_and_exit("No ASF UID stored in configuration.")
        return jwt_refresh(config_asf_uid)

    exp = payload.get("exp") or 0
    if exp < time.time():
        payload_asf_uid = payload.get("sub")
        if not payload_asf_uid:
            show.error_and_exit("No ASF UID in JWT payload.")
        if payload_asf_uid != config_asf_uid:
            # The user probably just changed their configuration
            # But we will refresh the JWT anyway
            # It will still fail if the PAT is not valid
            show.warning(f"JWT ASF UID {payload_asf_uid} does not match configuration ASF UID {config_asf_uid}")
        return jwt_refresh(payload_asf_uid)
    return jwt_value


@contextlib.contextmanager
def lock(write_to_disk: bool = False) -> Generator[dict[str, Any]]:
    lock = filelock.FileLock(str(path()) + ".lock")
    with lock:
        cfg = read()
        yield cfg
        if write_to_disk is True:
            write(cfg)


def path() -> pathlib.Path:
    if env := os.getenv("ATR_CLIENT_CONFIG_PATH"):
        return pathlib.Path(env).expanduser()
    return platformdirs.user_config_path("atr", appauthor="ASF") / "atr.yaml"


def read() -> dict[str, Any]:
    config_file = path()
    if config_file.exists():
        try:
            data = strictyaml.load(config_file.read_text(), YAML_SCHEMA).data
            if not isinstance(data, dict):
                raise RuntimeError("Invalid atr.yaml: not a dictionary")
            return data
        except strictyaml.YAMLValidationError as e:
            raise RuntimeError(f"Invalid atr.yaml: {e}") from e
    return copy.deepcopy(YAML_DEFAULTS)


def set_value(config: dict[str, Any], parts: list[str], val: Any) -> None:
    walk(config, parts, "set", val)


def walk(
    config: dict[str, Any],
    parts: list[str],
    op: Literal["drop", "get", "set"],
    value: Any | None = None,
) -> tuple[bool, Any | None]:
    match (op, parts):
        case ("get", [k, *tail]) if tail:
            # TODO: If config.get(k, {}) is not a dict, this fails
            return walk(config.get(k, {}), tail, op)
        case ("get", [k]):
            return (k in config), config.get(k)
        case ("set", [k, *tail]) if tail:
            child = config.setdefault(k, {})
            changed, _ = walk(child, tail, op, value)
            return changed, value
        case ("set", [k]):
            changed = config.get(k) != value
            config[k] = value
            return changed, value
        case ("drop", [k, *tail]) if tail:
            if (k not in config) or (not isinstance(config[k], dict)):
                return False, None
            changed, removed_value = walk(config[k], tail, op)
            if changed and not config[k]:
                config.pop(k)
            return changed, removed_value
        case ("drop", [k]):
            if k in config:
                removed_value = config.pop(k)
                return True, removed_value
            return False, None
    raise ValueError(f"Invalid operation: {op} with parts: {parts}")


def write(data: dict[str, Any]) -> None:
    data = {k: v for k, v in data.items() if not (isinstance(v, dict) and not v)}
    config_path = path()
    if not data:
        if config_path.exists():
            config_path.unlink()
        return
    tmp = config_path.with_suffix(".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(
        strictyaml.as_document(data, YAML_SCHEMA).as_yaml(),
        encoding="utf-8",
    )
    os.replace(tmp, config_path)
