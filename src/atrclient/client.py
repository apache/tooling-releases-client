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

# TODO: Allow upload and download by calling rsync
# Or potentially native for downloads, which should be trivial
# There is also https://github.com/synodriver/pyrsync

from __future__ import annotations

import asyncio
import base64
import contextlib
import copy
import datetime
import importlib.metadata as metadata
import json
import os
import pathlib
import re
import signal
import sys
import time
from typing import TYPE_CHECKING, Annotated, Any, Literal, NoReturn, TypeGuard, TypeVar

import aiohttp
import cyclopts
import filelock
import jwt
import platformdirs
import pydantic
import strictyaml

import atrclient.models as models

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Sequence

APP: cyclopts.App = cyclopts.App()
APP_CHECKS: cyclopts.App = cyclopts.App(name="checks", help="Check result operations.")
APP_CONFIG: cyclopts.App = cyclopts.App(name="config", help="Configuration operations.")
APP_DEV: cyclopts.App = cyclopts.App(name="dev", help="Developer operations.")
APP_DRAFT: cyclopts.App = cyclopts.App(name="draft", help="Draft operations.")
APP_JWT: cyclopts.App = cyclopts.App(name="jwt", help="JWT operations.")
APP_KEYS: cyclopts.App = cyclopts.App(name="keys", help="Keys operations.")
APP_RELEASE: cyclopts.App = cyclopts.App(name="release", help="Release operations.")
APP_SSH: cyclopts.App = cyclopts.App(name="ssh", help="SSH operations.")
APP_VOTE: cyclopts.App = cyclopts.App(name="vote", help="Vote operations.")
VERSION: str = metadata.version("apache-trusted-releases")
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

JSON = dict[str, Any] | list[Any] | str | int | float | bool | None


class ApiCore:
    def __init__(self, path: str):
        host, verify_ssl = config_host_get()
        self.url = f"https://{host}/api{path}"
        self.verify_ssl = verify_ssl


class ApiGet(ApiCore):
    def get(self, *args: str, **kwargs: str | None) -> JSON:
        url = self.url + "/" + "/".join(args)
        for value in kwargs.values():
            if value is not None:
                url += f"/{value}"
        jwt_value = None
        return asyncio.run(web_get(url, jwt_value, self.verify_ssl))


class ApiPost(ApiCore):
    def post(self, args: models.schema.Strict) -> JSON:
        jwt_value = config_jwt_usable()
        return asyncio.run(web_post(self.url, args, jwt_value, self.verify_ssl))


A = TypeVar("A", bound=models.schema.Strict)
R = TypeVar("R", bound=models.api.Results)


def api_get(path: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        def wrapper(*args: str, **kwargs: str | None) -> R:
            api_instance = ApiGet(path)
            try:
                response = func(api_instance, *args, **kwargs)
            except (pydantic.ValidationError, models.api.ResultsTypeError) as e:
                show_error_and_exit(f"Unexpected API GET response: {e}")
            return response

        return wrapper

    return decorator


def api_post(path: str) -> Callable[[Callable[[ApiPost, A], R]], Callable[[A], R]]:
    def decorator(func: Callable[[ApiPost, A], R]) -> Callable[[A], R]:
        def wrapper(args: A) -> R:
            api_instance = ApiPost(path)
            try:
                response = func(api_instance, args)
            except (pydantic.ValidationError, models.api.ResultsTypeError) as e:
                show_error_and_exit(f"Unexpected API POST response: {e}")
            return response

        return wrapper

    return decorator


@api_post("/announce")
def api_announce(api: ApiPost, args: models.api.AnnounceArgs) -> models.api.AnnounceResults:
    response = api.post(args)
    return models.api.validate_announce(response)


@api_get("/checks/list")
def api_checks_list(api: ApiGet, project: str, version: str, revision: str) -> models.api.ChecksListResults:
    response = api.get(project, version, revision)
    return models.api.validate_checks_list(response)


@api_get("/checks/ongoing")
def api_checks_ongoing(
    api: ApiGet, project: str, version: str, revision: str | None = None
) -> models.api.ChecksOngoingResults:
    response = api.get(project, version, revision=revision)
    return models.api.validate_checks_ongoing(response)


@api_post("/draft/delete")
def api_draft_delete(api: ApiPost, args: models.api.DraftDeleteArgs) -> models.api.DraftDeleteResults:
    response = api.post(args)
    return models.api.validate_draft_delete(response)


@api_post("/keys/add")
def api_keys_add(api: ApiPost, args: models.api.KeysAddArgs) -> models.api.KeysAddResults:
    response = api.post(args)
    return models.api.validate_keys_add(response)


@api_post("/keys/delete")
def api_keys_delete(api: ApiPost, args: models.api.KeysDeleteArgs) -> models.api.KeysDeleteResults:
    response = api.post(args)
    return models.api.validate_keys_delete(response)


@api_get("/keys/get")
def api_keys_get(api: ApiGet, fingerprint: str) -> models.api.KeysGetResults:
    response = api.get(fingerprint)
    return models.api.validate_keys_get(response)


@api_post("/keys/upload")
def api_keys_upload(api: ApiPost, args: models.api.KeysUploadArgs) -> models.api.KeysUploadResults:
    response = api.post(args)
    return models.api.validate_keys_upload(response)


@api_get("/keys/user")
def api_keys_user(api: ApiGet, asf_uid: str) -> models.api.KeysUserResults:
    response = api.get(asf_uid)
    return models.api.validate_keys_user(response)


@api_get("/list")
def api_list(api: ApiGet, project: str, version: str) -> models.api.ListResults:
    response = api.get(project, version)
    return models.api.validate_list(response)


@api_post("/releases/create")
def api_releases_create(api: ApiPost, args: models.api.ReleasesCreateArgs) -> models.api.ReleasesCreateResults:
    response = api.post(args)
    return models.api.validate_releases_create(response)


@api_post("/releases/delete")
def api_releases_delete(api: ApiPost, args: models.api.ReleasesDeleteArgs) -> models.api.ReleasesDeleteResults:
    response = api.post(args)
    return models.api.validate_releases_delete(response)


@api_get("/releases/project")
def api_releases_project(api: ApiGet, project: str) -> models.api.ReleasesProjectResults:
    response = api.get(project)
    return models.api.validate_releases_project(response)


@api_get("/releases/version")
def api_releases_version(api: ApiGet, project: str, version: str) -> models.api.ReleasesVersionResults:
    response = api.get(project, version)
    return models.api.validate_releases_version(response)


@api_get("/revisions")
def api_revisions(api: ApiGet, project: str, version: str) -> models.api.RevisionsResults:
    response = api.get(project, version)
    return models.api.validate_revisions(response)


@api_post("/ssh/add")
def api_ssh_add(api: ApiPost, args: models.api.SshAddArgs) -> models.api.SshAddResults:
    response = api.post(args)
    return models.api.validate_ssh_add(response)


@api_post("/ssh/delete")
def api_ssh_delete(api: ApiPost, args: models.api.SshDeleteArgs) -> models.api.SshDeleteResults:
    response = api.post(args)
    return models.api.validate_ssh_delete(response)


@api_get("/ssh/list")
def api_ssh_list(api: ApiGet, asf_uid: str) -> models.api.SshListResults:
    response = api.get(asf_uid)
    return models.api.validate_ssh_list(response)


@api_post("/upload")
def api_upload(api: ApiPost, args: models.api.UploadArgs) -> models.api.UploadResults:
    response = api.post(args)
    return models.api.validate_upload(response)


@api_post("/vote/resolve")
def api_vote_resolve(api: ApiPost, args: models.api.VoteResolveArgs) -> models.api.VoteResolveResults:
    response = api.post(args)
    return models.api.validate_vote_resolve(response)


@api_post("/vote/start")
def api_vote_start(api: ApiPost, args: models.api.VoteStartArgs) -> models.api.VoteStartResults:
    response = api.post(args)
    return models.api.validate_vote_start(response)


@APP.command(name="announce", help="Announce a release.")
def app_announce(
    project: str,
    version: str,
    revision: str,
    /,
    mailing_list: Annotated[str, cyclopts.Parameter(alias="-m", name="--mailing-list")],
    subject: Annotated[str | None, cyclopts.Parameter(alias="-s", name="--subject")] = None,
    body: Annotated[str | None, cyclopts.Parameter(alias="-b", name="--body")] = None,
    path_suffix: Annotated[str | None, cyclopts.Parameter(alias="-p", name="--path-suffix")] = None,
) -> None:
    announce_args = models.api.AnnounceArgs(
        project=project,
        version=version,
        revision=revision,
        email_to=mailing_list,
        subject=subject or f"[ANNOUNCE] Release {project} {version}",
        body=body or f"Release {project} {version} has been announced.",
        path_suffix=path_suffix or "",
    )
    announce = api_announce(announce_args)
    print(announce.success)


@APP_CHECKS.command(name="exceptions", help="Get check exceptions for a release revision.")
def app_checks_exceptions(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    checks_list = api_checks_list(project, version, revision)
    checks_display_status("exception", checks_list.checks, members=members)


@APP_CHECKS.command(name="failures", help="Get check failures for a release revision.")
def app_checks_failures(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    checks_list = api_checks_list(project, version, revision)
    checks_display_status("failure", checks_list.checks, members=members)


@APP_CHECKS.command(name="status", help="Get check status for a release revision.")
def app_checks_status(
    project: str,
    version: str,
    /,
    revision: str | None = None,
    verbose: Annotated[bool, cyclopts.Parameter(alias="-v", name="--verbose")] = False,
) -> None:
    releases_version = api_releases_version(project, version)
    release = releases_version.release
    # TODO: Handle the not found case better
    if release.phase != "release_candidate_draft":
        print("Checks are not applicable for this release phase.")
        print("Checks are only performed during the draft phase.")
        return

    if revision is None:
        if release.latest_revision_number is None:
            show_error_and_exit("No revision number found.")
        if not isinstance(release.latest_revision_number, str):
            show_error_and_exit(f"Unexpected API response: {release.latest_revision_number}")
        revision = release.latest_revision_number

    checks_list = api_checks_list(project, version, revision)
    checks_display(checks_list.checks, verbose)


@APP_CHECKS.command(name="wait", help="Wait for checks to be completed.")
def app_checks_wait(
    project: str,
    version: str,
    /,
    revision: str | None = None,
    timeout: Annotated[float, cyclopts.Parameter(alias="-t", name="--timeout")] = 60,
    interval: Annotated[int, cyclopts.Parameter(alias="-i", name="--interval")] = 500,
) -> None:
    _host, verify_ssl = config_host_get()
    if verify_ssl is True:
        if interval < 500:
            show_error_and_exit("Interval must be at least 500ms.")
    interval_seconds = interval / 1000
    if interval_seconds > timeout:
        show_error_and_exit("Interval must be less than timeout.")
    while True:
        checks_ongoing = api_checks_ongoing(project, version, revision)
        if checks_ongoing.ongoing == 0:
            break
        time.sleep(interval_seconds)
        timeout -= interval_seconds
        if timeout <= 0:
            show_error_and_exit("Timeout waiting for checks to complete.")
    print("Checks completed.")


@APP_CHECKS.command(name="warnings", help="Get check warnings for a release revision.")
def app_checks_warnings(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    checks_list = api_checks_list(project, version, revision)
    checks_display_status("warning", checks_list.checks, members=members)


@APP_CONFIG.command(name="file", help="Display the configuration file contents.")
def app_config_file() -> None:
    path = config_path()
    if not path.exists():
        show_error_and_exit("No configuration file found.")

    with path.open("r", encoding="utf-8") as fh:
        for chunk in fh:
            print(chunk, end="")


@APP_CONFIG.command(name="path", help="Show the configuration file path.")
def app_config_path() -> None:
    print(config_path())


@APP_DEV.command(name="delete", help="Delete a release.")
def app_dev_delete(project: str, version: str, /) -> None:
    releases_delete_args = models.api.ReleasesDeleteArgs(project=project, version=version)
    release_delete = api_releases_delete(releases_delete_args)
    print(release_delete.deleted)


@APP_DEV.command(name="env", help="Show the environment variables.")
def app_dev_env() -> None:
    total = 0
    for key, value in sorted(os.environ.items()):
        if not key.startswith("ATR_"):
            continue
        print(f"{key}={json.dumps(value, indent=None)}")
        total += 1
    print(f"There are {total} ATR_* environment variables.")


@APP_DEV.command(name="key", help="Return a test OpenPGP key.")
def app_dev_key() -> None:
    with open("tooling-public-test.asc", "w") as w:
        w.write("""\
-----BEGIN PGP PUBLIC KEY BLOCK-----

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
Qx20dp/Ekji4w6nAtopc4CTjL7YeRFdBKQ==
=CTh1
-----END PGP PUBLIC KEY BLOCK-----
""")


@APP_DEV.command(name="pat", help="Read a PAT from development configuration.")
def app_dev_pat() -> None:
    atr_pat_path = pathlib.Path.home() / ".atr-pat"
    if not atr_pat_path.exists():
        show_error_and_exit("~/.atr-pat not found.")
    text = atr_pat_path.read_text(encoding="utf-8").removesuffix("\n")
    print(text)


@APP_DEV.command(name="pwd", help="Show the current working directory.")
def app_dev_pwd() -> None:
    print(os.getcwd())


@APP_DEV.command(name="stamp", help="Update version and exclude-newer in pyproject.toml.")
def app_dev_stamp() -> None:
    path = pathlib.Path("pyproject.toml")
    if not path.exists():
        show_error_and_exit("pyproject.toml not found.")

    text_v1 = path.read_text()

    v = datetime.datetime.now(datetime.UTC).strftime("0.%Y%m%d.%H%M")
    text_v2 = re.sub(r"0\.\d{8}\.\d{4}", v, text_v1)
    version_updated = not (text_v1 == text_v2)

    ts = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:00Z")
    text_v3 = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ts, text_v2)
    exclude_newer_updated = not (text_v2 == text_v3)

    if version_updated or exclude_newer_updated:
        path.write_text(text_v3, "utf-8")
    print("Updated exclude-newer." if exclude_newer_updated else "Did not update exclude-newer.")
    print("Updated version." if version_updated else "Did not update version.")

    path = pathlib.Path("tests/cli_version.t")
    if not path.exists():
        show_warning("tests/cli_version.t not found.")
        return
    text_v1 = path.read_text(encoding="utf-8")
    text_v2 = re.sub(r"0\.\d{8}\.\d{4}", v, text_v1)
    version_updated = not (text_v1 == text_v2)
    if version_updated:
        path.write_text(text_v2, "utf-8")
        print("Updated tests/cli_version.t.")


@APP_DEV.command(name="token", help="Generate a random alphabetical token.")
def app_dev_token() -> None:
    import secrets

    label = ""
    # int(math.log2(26 ** 16)) == 75
    while len(label) < 16:
        i = secrets.randbits(5)
        # Do not use modulo here
        if i < 26:
            label += chr(i + 97)
    print(label)


@APP_DEV.command(name="user", help="Show the value of $USER.")
def app_dev_user() -> None:
    # This does not help if your ASF UID is not the same as $USER
    print(os.environ["USER"])


@APP_DRAFT.command(name="delete", help="Delete a draft release.")
def app_draft_delete(project: str, version: str, /) -> None:
    draft_delete_args = models.api.DraftDeleteArgs(project=project, version=version)
    draft_delete = api_draft_delete(draft_delete_args)
    print(draft_delete.success)


@APP.command(name="docs", help="Show comprehensive CLI documentation in Markdown.")
def app_docs() -> None:
    old_help_format = APP.help_format
    APP.help_format = "markdown"
    markdown = documentation_to_markdown(APP)
    APP.help_format = old_help_format
    print(markdown.rstrip())


@APP.command(name="drop", help="Remove a configuration key using dot notation.")
def app_drop(path: str, /) -> None:
    parts = path.split(".")
    if not parts:
        show_error_and_exit("Not a valid configuration key")

    with config_lock(write=True) as config:
        present, _ = config_walk(config, parts, "drop")
        if not present:
            show_error_and_exit(f"Could not find {path} in the configuration file")

    print(f"Removed {path}.")


@APP_JWT.command(name="dump", help="Show decoded JWT payload from stored config.")
def app_jwt_dump() -> None:
    jwt_value = config_jwt_get()
    if jwt_value is None:
        show_error_and_exit("No JWT stored in configuration.")

    header = jwt.get_unverified_header(jwt_value)
    if header != {"alg": "HS256", "typ": "JWT"}:
        show_error_and_exit("Invalid JWT header.")

    try:
        payload = jwt.decode(jwt_value, options={"verify_signature": False})
    except jwt.PyJWTError as e:
        show_error_and_exit(f"Failed to decode JWT: {e}")

    print(json.dumps(payload, indent=None))


@APP_JWT.command(name="info", help="Show JWT payload in human-readable form.")
def app_jwt_info() -> None:
    jwt_value, payload = config_jwt_payload()
    if jwt_value is None:
        show_error_and_exit("No JWT stored in configuration.")

    lines: list[str] = []
    for key, val in payload.items():
        if key in ("exp", "iat", "nbf"):
            val = timestamp_format(val)
        lines.append(f"{key.title()}: {val}")

    print("\n".join(lines))


@APP_JWT.command(name="refresh", help="Fetch a JWT using the stored PAT and store it in config.")
def app_jwt_refresh(asf_uid: str | None = None) -> None:
    jwt_value = config_jwt_refresh(asf_uid)
    print(jwt_value)


@APP_JWT.command(name="show", help="Show stored JWT token.")
def app_jwt_show() -> None:
    return app_show("tokens.jwt")


@APP_KEYS.command(name="add", help="Add an OpenPGP key.")
def app_keys_add(path: str, committees: str = "", /) -> None:
    selected_committee_names = []
    if committees:
        selected_committee_names[:] = committees.split(",")
    key = pathlib.Path(path).read_text(encoding="utf-8")
    with config_lock() as config:
        asf_uid = config_get(config, ["asf", "uid"])
    if asf_uid is None:
        show_error_and_exit("Please configure asf.uid before adding a key.")
    keys_add_args = models.api.KeysAddArgs(asfuid=asf_uid, key=key, committees=selected_committee_names)
    keys_add = api_keys_add(keys_add_args)
    for fingerprint in keys_add.fingerprints:
        print(fingerprint)


@APP_KEYS.command(name="delete", help="Delete an OpenPGP key.")
def app_keys_delete(fingerprint: str, /) -> None:
    keys_delete_args = models.api.KeysDeleteArgs(fingerprint=fingerprint)
    keys_delete = api_keys_delete(keys_delete_args)
    print(keys_delete.success)


@APP_KEYS.command(name="get", help="Get an OpenPGP key.")
def app_keys_get(fingerprint: str, /) -> None:
    keys_get = api_keys_get(fingerprint)
    print(keys_get.key.model_dump_json(indent=None))


@APP_KEYS.command(name="upload", help="Upload a KEYS file.")
def app_keys_upload(path: str, selected_committees: str, /) -> None:
    selected_committee_names = []
    if selected_committees:
        selected_committee_names[:] = selected_committees.split(",")
    key = pathlib.Path(path).read_text(encoding="utf-8")
    keys_upload_args = models.api.KeysUploadArgs(filetext=key, committees=selected_committee_names)
    keys_upload = api_keys_upload(keys_upload_args)
    for result in keys_upload.results:
        print(result.model_dump_json(indent=None))
    print(f"Successfully uploaded {keys_upload.success_count} keys.")
    print(f"Failed to upload {keys_upload.error_count} keys.")


@APP_KEYS.command(name="user", help="List OpenPGP keys for a user.")
def app_keys_user(asf_uid: str | None = None) -> None:
    if asf_uid is None:
        with config_lock() as config:
            asf_uid = config_get(config, ["asf", "uid"])
    if asf_uid is None:
        show_error_and_exit("No ASF UID provided and asf.uid not configured.")
    keys_user = api_keys_user(asf_uid)
    for key in keys_user.keys:
        print(key.model_dump_json(indent=None))


@APP.command(name="list", help="List all files within a release.")
def app_list(project: str, version: str, revision: str | None = None, /) -> None:
    list_results = api_list(project, version, revision)
    for rel_path in list_results.rel_paths:
        print(rel_path)


@APP_RELEASE.command(name="info", help="Show information about a release.")
def app_release_info(project: str, version: str, /) -> None:
    releases_version = api_releases_version(project, version)
    print(releases_version.release.model_dump_json(indent=None))


@APP_RELEASE.command(name="list", help="List releases for a project.")
def app_release_list(project: str, /) -> None:
    # TODO: Support showing all of a user's releases if no project is provided
    releases_project = api_releases_project(project)
    releases_display(releases_project.data)


@APP_RELEASE.command(name="start", help="Start a release.")
def app_release_start(project: str, version: str, /) -> None:
    releases_create_args = models.api.ReleasesCreateArgs(project=project, version=version)
    releases_create = api_releases_create(releases_create_args)
    print(releases_create.release.model_dump_json(indent=None))


@APP.command(name="revisions", help="List all revisions for a release.")
def app_revisions(project: str, version: str, /) -> None:
    revisions = api_revisions(project, version)
    for revision in revisions.revisions:
        print(revision)


@APP.command(name="set", help="Set a configuration value using dot notation.")
def app_set(path: str, value: str, /) -> None:
    parts = path.split(".")
    if not parts:
        show_error_and_exit("Not a valid configuration key.")

    with config_lock(write=True) as config:
        config_set(config, path.split("."), value)

    print(f"Set {path} to {json.dumps(value, indent=None)}.")


@APP.command(name="show", help="Show a configuration value using dot notation.")
def app_show(path: str, /) -> None:
    parts = path.split(".")
    if not parts:
        show_error_and_exit("Not a valid configuration key.")

    with config_lock() as config:
        value = config_get(config, parts)

    if value is None:
        show_error_and_exit(f"Could not find {path} in the configuration file.")

    print(value)


@APP_SSH.command(name="add", help="Add an SSH key.")
def app_ssh_add(text: str, /) -> None:
    ssh_add_args = models.api.SshAddArgs(text=text)
    ssh_add = api_ssh_add(ssh_add_args)
    print(ssh_add.fingerprint)


@APP_SSH.command(name="delete", help="Delete an SSH key.")
def app_ssh_delete(fingerprint: str, /) -> None:
    ssh_delete_args = models.api.SshDeleteArgs(fingerprint=fingerprint)
    ssh_delete = api_ssh_delete(ssh_delete_args)
    print(ssh_delete.success)


@APP_SSH.command(name="list", help="List SSH keys.")
def app_ssh_list(asf_uid: str | None = None) -> None:
    if asf_uid is None:
        with config_lock() as config:
            asf_uid = config_get(config, ["asf", "uid"])
    if asf_uid is None:
        show_error_and_exit("No ASF UID provided and asf.uid not configured.")
    ssh_list = api_ssh_list(asf_uid)
    print(ssh_list.data)


@APP.command(name="upload", help="Upload a file to a release.")
def app_upload(project: str, version: str, path: str, filepath: str, /) -> None:
    with open(filepath, "rb") as fh:
        content = fh.read()

    upload_args = models.api.UploadArgs(
        project=project,
        version=version,
        relpath=path,
        content=base64.b64encode(content).decode("utf-8"),
    )

    upload = api_upload(upload_args)
    print(upload.revision.model_dump_json(indent=None))


@APP_VOTE.command(name="resolve", help="Resolve a vote.")
def app_vote_resolve(
    project: str,
    version: str,
    resolution: Literal["passed", "failed"],
) -> None:
    vote_resolve_args = models.api.VoteResolveArgs(
        project=project,
        version=version,
        resolution=resolution,
    )
    vote_resolve = api_vote_resolve(vote_resolve_args)
    print(vote_resolve.success)


@APP_VOTE.command(name="start", help="Start a vote.")
def app_vote_start(
    project: str,
    version: str,
    revision: str,
    /,
    mailing_list: Annotated[str, cyclopts.Parameter(alias="-m", name="--mailing-list")],
    duration: Annotated[int, cyclopts.Parameter(alias="-d", name="--duration")] = 72,
    subject: Annotated[str | None, cyclopts.Parameter(alias="-s", name="--subject")] = None,
    body: Annotated[str | None, cyclopts.Parameter(alias="-b", name="--body")] = None,
) -> None:
    body_text = None
    if body:
        with open(body, encoding="utf-8") as fh:
            body_text = fh.read()

    vote_start_args = models.api.VoteStartArgs(
        project=project,
        version=version,
        revision=revision,
        email_to=mailing_list,
        vote_duration=duration,
        subject=subject or f"[VOTE] Release {project} {version}",
        body=body_text or f"Release {project} {version} is ready for voting.",
    )
    vote_start = api_vote_start(vote_start_args)
    print(vote_start.task.model_dump_json(indent=None))


def checks_display(results: Sequence[models.sql.CheckResult], verbose: bool = False) -> None:
    if not results:
        print("No check results found for this revision.")
        return

    by_status: dict[str, list[models.sql.CheckResult]] = {}
    for result in results:
        status = result.status
        by_status.setdefault(status, []).append(result)

    checks_display_summary(by_status, verbose, len(results))
    checks_display_details(by_status, verbose)


def checks_display_details(by_status: dict[str, list[models.sql.CheckResult]], verbose: bool) -> None:
    if not verbose:
        return
    for status_key in by_status.keys():
        if status_key.upper() not in ["FAILURE", "EXCEPTION", "WARNING"]:
            continue
        print(f"\n{status_key}:")
        checks_display_verbose_details(by_status[status_key])


def checks_display_status(
    status: Literal["failure", "exception", "warning"],
    results: Sequence[models.sql.CheckResult],
    members: bool,
) -> None:
    messages = {}
    for result in results:
        if result.status != status:
            continue
        member_rel_path = result.member_rel_path
        if member_rel_path and (not members):
            continue
        checker = result.checker or ""
        message = result.message
        primary_rel_path = result.primary_rel_path
        if not member_rel_path:
            path = primary_rel_path
        else:
            path = f"{primary_rel_path} → {member_rel_path}"

        if path not in messages:
            messages[path] = []
        msg = f" - {message} ({checker.removeprefix('atr.tasks.checks.')})"
        messages[path].append(msg)

    for path in sorted(messages):
        print(path)
        for msg in sorted(messages[path]):
            print(msg)
        print()


def checks_display_summary(by_status: dict[str, list[models.sql.CheckResult]], verbose: bool, total: int) -> None:
    print(f"Total checks: {total}")
    for status, checks in by_status.items():
        if verbose and status.upper() in ["FAILURE", "EXCEPTION", "WARNING"]:
            top = sum(r.member_rel_path is None for r in checks)
            inner = len(checks) - top
            print(f"  {status}: {len(checks)} (top-level {top}, inner {inner})")
        else:
            print(f"  {status}: {len(checks)}")


def checks_display_verbose_details(checks: Sequence[models.sql.CheckResult]) -> None:
    for check in checks[:10]:
        checker = check.checker or ""
        primary_rel_path = check.primary_rel_path or ""
        member_rel_path = check.member_rel_path or ""
        message = check.message
        member_part = f" ({member_rel_path})" if member_rel_path else ""
        print(f"  {checker} → {primary_rel_path}{member_part} : {message}")


def config_drop(config: dict[str, Any], parts: list[str]) -> None:
    config_walk(config, parts, "drop")


def config_get(config: dict[str, Any], parts: list[str]) -> Any | None:
    return config_walk(config, parts, "get")[1]


def config_host_get() -> tuple[str, bool]:
    with config_lock() as config:
        host = config.get("atr", {}).get("host", "release-test.apache.org")
    verify_ssl = not ((host == "127.0.0.1") or host.startswith("127.0.0.1:"))
    return host, verify_ssl


def config_jwt_get() -> str | None:
    with config_lock() as config:
        jwt_value = config_get(config, ["tokens", "jwt"])
    return jwt_value


def config_jwt_payload() -> tuple[str | None, dict[str, Any]]:
    jwt_value = config_jwt_get()
    if jwt_value is None:
        return None, {}
    if jwt_value == "dummy_jwt_token":
        # TODO: Use a better test JWT
        return jwt_value, {"exp": time.time() + 90 * 60, "sub": "test_asf_uid"}

    try:
        payload = jwt.decode(jwt_value, options={"verify_signature": False})
    except jwt.PyJWTError as e:
        show_error_and_exit(f"Failed to decode JWT: {e}")
    if not isinstance(payload, dict):
        show_error_and_exit("Invalid JWT payload.")
    return jwt_value, payload


def config_jwt_refresh(asf_uid: str | None = None) -> str:
    with config_lock() as config:
        pat_value = config_get(config, ["tokens", "pat"])
        if asf_uid is None:
            asf_uid = config.get("asf", {}).get("uid")

    if pat_value is None:
        show_error_and_exit("No Personal Access Token stored.")
    if asf_uid is None:
        show_error_and_exit("No ASF UID provided and asf.uid not configured.")

    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/jwt"
    args = models.api.JwtArgs(asfuid=asf_uid, pat=pat_value)
    response = asyncio.run(web_post(url, args, jwt_token=None, verify_ssl=verify_ssl))
    try:
        jwt_results = models.api.validate_jwt(response)
    except (pydantic.ValidationError, models.api.ResultsTypeError) as e:
        show_error_and_exit(f"Unexpected API response: {response}\n{e}")

    with config_lock(write=True) as config:
        config_set(config, ["tokens", "jwt"], jwt_results.jwt)

    return jwt_results.jwt


def config_jwt_usable() -> str:
    with config_lock() as config:
        config_asf_uid = config_get(config, ["asf", "uid"])

    jwt_value, payload = config_jwt_payload()
    if jwt_value is None:
        if config_asf_uid is None:
            show_error_and_exit("No ASF UID stored in configuration.")
        return config_jwt_refresh(config_asf_uid)

    exp = payload.get("exp") or 0
    if exp < time.time():
        payload_asf_uid = payload.get("sub")
        if not payload_asf_uid:
            show_error_and_exit("No ASF UID in JWT payload.")
        if payload_asf_uid != config_asf_uid:
            # The user probably just changed their configuration
            # But we will refresh the JWT anyway
            # It will still fail if the PAT is not valid
            show_warning(f"JWT ASF UID {payload_asf_uid} does not match configuration ASF UID {config_asf_uid}")
        return config_jwt_refresh(payload_asf_uid)
    return jwt_value


@contextlib.contextmanager
def config_lock(write: bool = False) -> Generator[dict[str, Any]]:
    lock = filelock.FileLock(str(config_path()) + ".lock")
    with lock:
        config = config_read()
        yield config
        if write is True:
            config_write(config)


def config_path() -> pathlib.Path:
    if env := os.getenv("ATR_CLIENT_CONFIG_PATH"):
        return pathlib.Path(env).expanduser()
    return platformdirs.user_config_path("atr", appauthor="ASF") / "atr.yaml"


def config_read() -> dict[str, Any]:
    config_file = config_path()
    if config_file.exists():
        try:
            data = strictyaml.load(config_file.read_text(), YAML_SCHEMA).data
            if not isinstance(data, dict):
                raise RuntimeError("Invalid atr.yaml: not a dictionary")
            return data
        except strictyaml.YAMLValidationError as e:
            raise RuntimeError(f"Invalid atr.yaml: {e}") from e
    return copy.deepcopy(YAML_DEFAULTS)


def config_set(config: dict[str, Any], parts: list[str], val: Any) -> None:
    config_walk(config, parts, "set", val)


def config_walk(
    config: dict[str, Any],
    parts: list[str],
    op: Literal["drop", "get", "set"],
    value: Any | None = None,
) -> tuple[bool, Any | None]:
    match (op, parts):
        case ("get", [k, *tail]) if tail:
            # TODO: If config.get(k, {}) is not a dict, this fails
            return config_walk(config.get(k, {}), tail, op)
        case ("get", [k]):
            return (k in config), config.get(k)
        case ("set", [k, *tail]) if tail:
            child = config.setdefault(k, {})
            changed, _ = config_walk(child, tail, op, value)
            return changed, value
        case ("set", [k]):
            changed = config.get(k) != value
            config[k] = value
            return changed, value
        case ("drop", [k, *tail]) if tail:
            if (k not in config) or (not isinstance(config[k], dict)):
                return False, None
            changed, removed_value = config_walk(config[k], tail, op)
            if changed and not config[k]:
                config.pop(k)
            return changed, removed_value
        case ("drop", [k]):
            if k in config:
                removed_value = config.pop(k)
                return True, removed_value
            return False, None
    raise ValueError(f"Invalid operation: {op} with parts: {parts}")


def config_write(data: dict[str, Any]) -> None:
    data = {k: v for k, v in data.items() if not (isinstance(v, dict) and not v)}
    path = config_path()
    if not data:
        if path.exists():
            path.unlink()
        return
    tmp = path.with_suffix(".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(
        strictyaml.as_document(data, YAML_SCHEMA).as_yaml(),
        encoding="utf-8",
    )
    os.replace(tmp, path)


def documentation_to_markdown(
    app: cyclopts.App,
    subcommands: list[str] | None = None,
    seen: set[str] | None = None,
) -> str:
    import io

    import rich.console as console

    seen = seen or set()
    string_io = io.StringIO()
    rich_console = console.Console(record=True, width=120, file=string_io)
    original_console = app.console
    app.console = rich_console
    with contextlib.redirect_stdout(string_io):
        app.help_print()
    app.console = original_console

    exported_text = rich_console.export_text()
    if not subcommands:
        subcommands = [" ".join(app.name) if isinstance(app.name, list | tuple) else (app.name or "atr")]
    level = len(subcommands)
    markdown = f"""
{"#" * level} {" ".join(subcommands)}

```
{exported_text.rstrip()}
```
"""
    commands = sorted(app)
    for cmd in commands:
        if cmd in seen or cmd.startswith("-"):
            continue
        sub = app[cmd]
        if isinstance(sub, cyclopts.App):
            seen.add(cmd)
            markdown += documentation_to_markdown(sub, [*subcommands, cmd], seen)
    return markdown


def initialise() -> None:
    # We do this because pytest_console_scripts.ScriptRunner invokes main multiple times
    APP.version = VERSION
    if sys.platform not in {"cygwin", "win32"}:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    subcommands_register(APP)


def initialised() -> bool:
    return APP.version == VERSION


def is_json(data: Any) -> TypeGuard[JSON]:
    if isinstance(data, str | int | float | bool | None):
        return True
    if isinstance(data, dict):
        if any(not isinstance(key, str) for key in data):
            return False
        return all(is_json(value) for value in data.values())
    if isinstance(data, list):
        return all(is_json(item) for item in data)
    return False


def is_json_dict(data: JSON) -> TypeGuard[dict[str, JSON]]:
    # The keys are already validated due to it being a JSON object
    return isinstance(data, dict)


def is_json_list(data: JSON) -> TypeGuard[list[JSON]]:
    # The items are already validated due to it being a JSON array
    return isinstance(data, list)


def is_json_list_of_dict(data: JSON) -> TypeGuard[list[dict[str, JSON]]]:
    return is_json_list(data) and all(is_json_dict(item) for item in data)


def iso_to_human(ts: str) -> str:
    dt = datetime.datetime.fromisoformat(ts.rstrip("Z"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.UTC)
    return dt.strftime("%Y-%m-%d %H:%MZ")


def main() -> None:
    if not initialised():
        initialise()
    # if "PYTEST_CURRENT_TEST" in os.environ:
    #     # "Cyclopts application invoked without tokens"
    #     pass
    APP(sys.argv[1:])


def releases_display(releases: Sequence[models.sql.Release]) -> None:
    if not releases:
        print("No releases found for this project.")
        return

    print(f"Total releases: {len(releases)}")
    print(f"  {'Version':<24} {'Latest':<7} {'Phase':<11} {'Created'}")
    for release in releases:
        version = release.version
        phase = release.phase
        # if not isinstance(version, str):
        #     show_warning(f"Unexpected API response: {release}")
        #     continue
        phase_short = {
            "release_candidate_draft": "draft",
            "release_candidate": "candidate",
            "release_preview": "preview",
            "release": "finished",
        }.get(phase, "unknown")
        if release.created:
            created_iso = release.created.isoformat()
            created_formatted = iso_to_human(created_iso)
        else:
            created_formatted = "Unknown"
        latest = release.latest_revision_number or "-"
        print(f"  {version:<24} {latest:<7} {phase_short:<11} {created_formatted}")


def show_error_and_exit(message: str, code: int = 1) -> NoReturn:
    sys.stderr.write(f"atr: error: {message}\n")
    sys.stderr.flush()
    raise SystemExit(code)


def show_warning(message: str) -> None:
    sys.stderr.write(f"atr: warning: {message}\n")
    sys.stderr.flush()


def subcommands_register(app: cyclopts.App) -> None:
    app.command(APP_CHECKS)
    app.command(APP_CONFIG)
    app.command(APP_DEV)
    app.command(APP_DRAFT)
    app.command(APP_JWT)
    app.command(APP_KEYS)
    app.command(APP_RELEASE)
    app.command(APP_SSH)
    app.command(APP_VOTE)


def timestamp_format(ts: int | str | None) -> str | None:
    if ts is None:
        return None
    try:
        t = int(ts)
        dt = datetime.datetime.fromtimestamp(t, datetime.UTC)
        return dt.strftime("%d %b %Y at %H:%M:%S UTC")
    except Exception:
        return str(ts)


async def web_get(url: str, jwt_token: str | None, verify_ssl: bool = True) -> JSON:
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    headers = {}
    if jwt_token is not None:
        headers["Authorization"] = f"Bearer {jwt_token}"
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                try:
                    error_data = json.loads(text)
                    if isinstance(error_data, dict) and ("error" in error_data):
                        error_message = error_data["error"]
                        show_error_and_exit(f"{error_message} from {url}")
                    else:
                        show_error_and_exit(f"Request failed: {resp.status} {url}\n{text}")
                except json.JSONDecodeError:
                    show_error_and_exit(f"Request failed: {resp.status} {url}\n{text}")
            data = await resp.json()
            if not is_json(data):
                show_error_and_exit(f"Unexpected API response: {data}")
            return data


async def web_post(url: str, args: models.schema.Strict, jwt_token: str | None, verify_ssl: bool = True) -> JSON:
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    headers = {}
    if jwt_token is not None:
        headers["Authorization"] = f"Bearer {jwt_token}"
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        async with session.post(url, json=args.model_dump()) as resp:
            if resp.status not in (200, 201):
                text = await resp.text()
                show_error_and_exit(f"Error message from the API:\n{resp.status} {url}\n{text}")

            try:
                data = await resp.json()
                if not is_json(data):
                    show_error_and_exit(f"Unexpected API response: {data}")
                return data
            except Exception as e:
                show_error_and_exit(f"Python error getting API response:\n{resp.status} {url}\n{e}")
