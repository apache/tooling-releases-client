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

# TODO: Use Pydantic models to validate API responses
# TODO: Use transcript style script testing

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
from typing import TYPE_CHECKING, Annotated, Any, Literal, NoReturn

import aiohttp
import cyclopts
import filelock
import jwt
import platformdirs
import strictyaml

if TYPE_CHECKING:
    from collections.abc import Generator

APP: cyclopts.App = cyclopts.App()
CHECKS: cyclopts.App = cyclopts.App(name="checks", help="Check result operations.")
CONFIG: cyclopts.App = cyclopts.App(name="config", help="Configuration operations.")
DEV: cyclopts.App = cyclopts.App(name="dev", help="Developer operations.")
DRAFT: cyclopts.App = cyclopts.App(name="draft", help="Draft operations.")
JWT: cyclopts.App = cyclopts.App(name="jwt", help="JWT operations.")
RELEASE: cyclopts.App = cyclopts.App(name="release", help="Release operations.")
VERSION: str = metadata.version("apache-trusted-releases")
VOTE: cyclopts.App = cyclopts.App(name="vote", help="Vote operations.")
YAML_DEFAULTS: dict[str, Any] = {"asf": {}, "atr": {}, "tokens": {}}
YAML_SCHEMA: strictyaml.Map = strictyaml.Map(
    {
        strictyaml.Optional("atr"): strictyaml.Map(
            {strictyaml.Optional("host"): strictyaml.Str()}
        ),
        strictyaml.Optional("asf"): strictyaml.Map(
            {strictyaml.Optional("uid"): strictyaml.Str()}
        ),
        strictyaml.Optional("tokens"): strictyaml.Map(
            {
                strictyaml.Optional("pat"): strictyaml.Str(),
                strictyaml.Optional("jwt"): strictyaml.Str(),
            }
        ),
    }
)


@CHECKS.command(name="exceptions", help="Get check exceptions for a release revision.")
def app_checks_exceptions(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/checks/{project}/{version}/{revision}"
    results = asyncio.run(web_get(url, jwt_value, verify_ssl))
    checks_display_status("exception", results, members=members)


@CHECKS.command(name="failures", help="Get check failures for a release revision.")
def app_checks_failures(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/checks/{project}/{version}/{revision}"
    results = asyncio.run(web_get(url, jwt_value, verify_ssl))
    checks_display_status("failure", results, members=members)


@CHECKS.command(name="status", help="Get check status for a release revision.")
def app_checks_status(
    project: str,
    version: str,
    revision: str,
    /,
    verbose: Annotated[bool, cyclopts.Parameter(alias="-v", name="--verbose")] = False,
) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()

    release_url = f"https://{host}/api/releases/{project}"
    releases_result = asyncio.run(web_get_public(release_url, verify_ssl))

    target_release = None
    for release in releases_result.get("data", []):
        if release.get("version") == version:
            target_release = release
            break

    if target_release is None:
        show_error_and_exit(f"Release {project}-{version} not found.")

    phase = target_release.get("phase")
    if phase != "release_candidate_draft":
        print("Checks are not applicable for this release phase.")
        print("Checks are only performed during the draft phase.")
        return

    url = f"https://{host}/api/checks/{project}/{version}/{revision}"
    results = asyncio.run(web_get(url, jwt_value, verify_ssl))

    checks_display(results, verbose)


@CHECKS.command(name="warnings", help="Get check warnings for a release revision.")
def app_checks_warnings(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/checks/{project}/{version}/{revision}"
    results = asyncio.run(web_get(url, jwt_value, verify_ssl))
    checks_display_status("warning", results, members=members)


@CONFIG.command(name="file", help="Display the configuration file contents.")
def app_config_file() -> None:
    path = config_path()
    if not path.exists():
        show_error_and_exit("No configuration file found.")

    with path.open("r", encoding="utf-8") as fh:
        for chunk in fh:
            print(chunk, end="")


@CONFIG.command(name="path", help="Show the configuration file path.")
def app_config_path() -> None:
    print(config_path())


@DEV.command(name="env", help="Show the environment variables.")
def app_dev_env() -> None:
    total = 0
    for key, value in sorted(os.environ.items()):
        if not key.startswith("ATR_"):
            continue
        print(f"{key}={json.dumps(value, indent=None)}")
        total += 1
    print(f"There are {total} ATR_* environment variables.")


@DEV.command(name="stamp", help="Update version and exclude-newer in pyproject.toml.")
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
    print(
        "Updated exclude-newer."
        if exclude_newer_updated
        else "Did not update exclude-newer."
    )
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


@JWT.command(name="dump", help="Show decoded JWT payload from stored config.")
def app_jwt_dump() -> None:
    jwt_value = config_jwt_get()

    header = jwt.get_unverified_header(jwt_value)
    if header != {"alg": "HS256", "typ": "JWT"}:
        show_error_and_exit("Invalid JWT header.")

    try:
        payload = jwt.decode(jwt_value, options={"verify_signature": False})
    except jwt.PyJWTError as e:
        show_error_and_exit(f"Failed to decode JWT: {e}")

    print(json.dumps(payload, indent=None))


@JWT.command(name="info", help="Show JWT payload in human-readable form.")
def app_jwt_info() -> None:
    _jwt_value, payload = config_jwt_payload()

    lines: list[str] = []
    for key, val in payload.items():
        if key in ("exp", "iat", "nbf"):
            val = timestamp_format(val)
        lines.append(f"{key.title()}: {val}")

    print("\n".join(lines))


@JWT.command(
    name="refresh", help="Fetch a JWT using the stored PAT and store it in config."
)
def app_jwt_refresh(asf_uid: str | None = None) -> None:
    jwt_value = config_jwt_refresh(asf_uid)
    print(jwt_value)


@JWT.command(name="show", help="Show stored JWT token.")
def app_jwt_show() -> None:
    return app_show("tokens.jwt")


@APP.command(name="list", help="List all files within a release.")
def app_list(project: str, version: str, revision: str | None = None, /) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/list/{project}/{version}"
    if revision:
        url += f"/{revision}"
    result = asyncio.run(web_get(url, jwt_value, verify_ssl))
    print(result)


@RELEASE.command(name="info", help="Show information about a release.")
def app_release_info(project: str, version: str, /) -> None:
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/releases/{project}/{version}"
    result = asyncio.run(web_get_public(url, verify_ssl))
    print(result)


@RELEASE.command(name="list", help="List releases for a project.")
def app_release_list(project: str, /) -> None:
    # TODO: Support showing all of a user's releases if no project is provided
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/releases/{project}"
    result = asyncio.run(web_get_public(url, verify_ssl))
    releases_display(result)


@RELEASE.command(name="start", help="Start a release.")
def app_release_start(project: str, version: str, /) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/releases/create"

    payload: dict[str, str] = {"project_name": project, "version": version}

    result = asyncio.run(web_post(url, payload, jwt_value, verify_ssl))
    print(result)


@APP.command(name="revisions", help="List all revisions for a release.")
def app_revisions(project: str, version: str, /) -> None:
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/revisions/{project}/{version}"
    result = asyncio.run(web_get_public(url, verify_ssl))
    for revision in result.get("revisions", []):
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


@APP.command(name="upload", help="Upload a file to a release.")
def app_upload(project: str, version: str, path: str, filepath: str, /) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/upload"

    with open(filepath, "rb") as f:
        content = f.read()

    payload: dict[str, str] = {
        "project_name": project,
        "version": version,
        "rel_path": path,
        "content": base64.b64encode(content).decode("utf-8"),
    }

    result = asyncio.run(web_post(url, payload, jwt_value, verify_ssl))
    print(result)


@VOTE.command(name="start", help="Start a vote.")
def app_vote_start(
    project: str,
    version: str,
    revision: str,
    /,
    mailing_list: str,
    duration: Annotated[int, cyclopts.Parameter(alias="-d", name="--duration")] = 72,
    subject: Annotated[
        str | None, cyclopts.Parameter(alias="-s", name="--subject")
    ] = None,
    body: Annotated[str | None, cyclopts.Parameter(alias="-b", name="--body")] = None,
) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/vote/start"
    body_text = None
    if body:
        with open(body, "r", encoding="utf-8") as f:
            body_text = f.read()
    payload: dict[str, Any] = {
        "project_name": project,
        "version": version,
        "revision": revision,
        "email_to": mailing_list,
        "vote_duration": duration,
        "subject": subject or f"[VOTE] Release {project} {version}",
        "body": body_text or f"Release {project} {version} is ready for voting.",
    }
    result = asyncio.run(web_post(url, payload, jwt_value, verify_ssl))
    print(result)


@DRAFT.command(name="delete", help="Delete a draft release.")
def app_draft_delete(project: str, version: str, /) -> None:
    jwt_value = config_jwt_usable()
    host, verify_ssl = config_host_get()
    payload: dict[str, str] = {"project_name": project, "version": version}
    url = f"https://{host}/api/draft/delete"
    result = asyncio.run(web_post(url, payload, jwt_value, verify_ssl))
    print(result)


def checks_display(results: list[dict[str, Any]], verbose: bool = False) -> None:
    if not results:
        print("No check results found for this revision.")
        return

    by_status = {}
    for result in results:
        status = result["status"]
        by_status.setdefault(status, []).append(result)

    checks_display_summary(by_status, verbose, len(results))
    checks_display_details(by_status, verbose)


def checks_display_details(
    by_status: dict[str, list[dict[str, Any]]], verbose: bool
) -> None:
    if not verbose:
        return
    for status_key in by_status.keys():
        if status_key.upper() not in ["FAILURE", "EXCEPTION", "WARNING"]:
            continue
        print(f"\n{status_key}:")
        checks_display_verbose_details(by_status[status_key])


def checks_display_status(
    status: Literal["failure", "exception", "warning"],
    results: list[dict[str, Any]],
    members: bool,
) -> None:
    messages = {}
    for result in results:
        result_status = result.get("status")
        if result_status != status:
            continue
        member_rel_path = result.get("member_rel_path")
        if member_rel_path and (not members):
            continue
        checker = result.get("checker") or ""
        message = result.get("message")
        primary_rel_path = result.get("primary_rel_path")
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


def checks_display_summary(
    by_status: dict[str, list[dict[str, Any]]], verbose: bool, total: int
) -> None:
    print(f"Total checks: {total}")
    for status, checks in by_status.items():
        if verbose and status.upper() in ["FAILURE", "EXCEPTION", "WARNING"]:
            top = sum(r["member_rel_path"] is None for r in checks)
            inner = len(checks) - top
            print(f"  {status}: {len(checks)} (top-level {top}, inner {inner})")
        else:
            print(f"  {status}: {len(checks)}")


def checks_display_verbose_details(checks: list[dict[str, Any]]) -> None:
    for check in checks[:10]:
        checker = check["checker"]
        primary_rel_path = check.get("primary_rel_path", "")
        member_rel_path = check.get("member_rel_path", "")
        message = check["message"]
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


def config_jwt_get() -> str:
    with config_lock() as config:
        jwt_value = config_get(config, ["tokens", "jwt"])

    if jwt_value is None:
        show_error_and_exit("No JWT stored in configuration.")

    return jwt_value


def config_jwt_payload() -> tuple[str, dict[str, Any]]:
    jwt_value = config_jwt_get()
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

    if pat_value is None:
        show_error_and_exit("No Personal Access Token stored.")

    host, verify_ssl = config_host_get()
    url = f"https://{host}/api/jwt"

    if asf_uid is None:
        asf_uid = config.get("asf", {}).get("uid")

    if asf_uid is None:
        show_error_and_exit("No ASF UID provided and asf.uid not configured.")

    jwt_token = asyncio.run(web_fetch(url, asf_uid, pat_value, verify_ssl))

    with config_lock(write=True) as config:
        config_set(config, ["tokens", "jwt"], jwt_token)

    return jwt_token


def config_jwt_usable() -> str:
    jwt_value, payload = config_jwt_payload()
    if (payload.get("exp") or 0) < time.time():
        asf_uid = payload.get("sub")
        jwt_value = config_jwt_refresh(asf_uid)
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
        subcommands = [
            " ".join(app.name)
            if isinstance(app.name, (list, tuple))
            else (app.name or "atr")
        ]
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
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    subcommands_register(APP)


def initialised() -> bool:
    return APP.version == VERSION


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


def releases_display(result: dict[str, Any]) -> None:
    if ("data" not in result) or ("count" not in result):
        show_error_and_exit("Invalid response format")

    releases = result["data"]
    count = result["count"]

    if not releases:
        print("No releases found for this project.")
        return

    print(f"Total releases: {count}")
    print(f"  {'Version':<24} {'Latest':<7} {'Phase':<11} {'Created'}")
    for release in releases:
        version = release.get("version", "Unknown")
        phase = release.get("phase", "Unknown")
        phase_short = {
            "release_candidate_draft": "draft",
            "release_candidate": "candidate",
            "release_preview": "preview",
            "release": "finished",
        }.get(phase, "unknown")
        created = release.get("created")
        created_formatted = iso_to_human(created) if created else "Unknown"
        latest = release.get("latest_revision_number") or "-"
        print(f"  {version:<24} {latest:<7} {phase_short:<11} {created_formatted}")


def show_error_and_exit(message: str, code: int = 1) -> NoReturn:
    sys.stderr.write(f"atr: error: {message}\n")
    sys.stderr.flush()
    raise SystemExit(code)


def show_warning(message: str) -> None:
    sys.stderr.write(f"atr: warning: {message}\n")
    sys.stderr.flush()


def subcommands_register(app: cyclopts.App) -> None:
    app.command(CHECKS)
    app.command(CONFIG)
    app.command(DEV)
    app.command(DRAFT)
    app.command(JWT)
    app.command(RELEASE)
    app.command(VOTE)


def timestamp_format(ts: int | str | None) -> str | None:
    if ts is None:
        return None
    try:
        t = int(ts)
        dt = datetime.datetime.fromtimestamp(t, datetime.UTC)
        return dt.strftime("%d %b %Y at %H:%M:%S UTC")
    except Exception:
        return str(ts)


async def web_fetch(
    url: str, asfuid: str, pat_token: str, verify_ssl: bool = True
) -> str:
    # TODO: This is PAT request specific
    # Should give this a more specific name
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        payload = {"asfuid": asfuid, "pat": pat_token}
        async with session.post(url, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                show_error_and_exit(f"JWT fetch failed: {resp.status} {text}")

            data: dict[str, Any] = await resp.json()
            if "jwt" in data:
                return data["jwt"]
            raise RuntimeError(f"Unexpected response: {data}")


async def web_get(url: str, jwt_token: str, verify_ssl: bool = True) -> Any:
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    headers = {"Authorization": f"Bearer {jwt_token}"}
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                try:
                    error_data = json.loads(text)
                    if isinstance(error_data, dict) and "error" in error_data:
                        show_error_and_exit(error_data["error"])
                    else:
                        show_error_and_exit(f"Request failed: {resp.status} {text}")
                except json.JSONDecodeError:
                    show_error_and_exit(f"Request failed: {resp.status} {text}")
            return await resp.json()


async def web_get_public(url: str, verify_ssl: bool = True) -> Any:
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                try:
                    error_data = json.loads(text)
                    if isinstance(error_data, dict) and "error" in error_data:
                        show_error_and_exit(error_data["error"])
                    else:
                        show_error_and_exit(f"Request failed: {resp.status} {text}")
                except json.JSONDecodeError:
                    show_error_and_exit(f"Request failed: {resp.status} {text}")
            return await resp.json()


async def web_post(
    url: str, payload: dict[str, Any], jwt_token: str, verify_ssl: bool = True
) -> Any:
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    headers = {"Authorization": f"Bearer {jwt_token}"}
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        async with session.post(url, json=payload) as resp:
            if resp.status not in (200, 201):
                text = await resp.text()
                show_error_and_exit(
                    f"Error message from the API:\n{resp.status} {url}\n{text}"
                )

            try:
                return await resp.json()
            except Exception:
                text = await resp.text()
                return text
