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
import datetime
import hashlib
import importlib.metadata as metadata
import io
import json
import os
import pathlib
import re
import signal
import sys
import time
from typing import TYPE_CHECKING, Annotated, Any, Literal

import cyclopts
import jwt
import pgpy

import atrclient.api as api
import atrclient.basic as basic
import atrclient.config as config
import atrclient.models as models
import atrclient.show as show
import atrclient.web as web

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

APP: cyclopts.App = cyclopts.App()
APP_CHECK: cyclopts.App = cyclopts.App(name="check", help="Check result operations.")
APP_CONFIG: cyclopts.App = cyclopts.App(name="config", help="Configuration operations.")
APP_DEV: cyclopts.App = cyclopts.App(name="dev", help="Developer operations.")
APP_DISTRIBUTION: cyclopts.App = cyclopts.App(name="distribution", help="Distribution operations.")
APP_DRAFT: cyclopts.App = cyclopts.App(name="draft", help="Draft operations.")
APP_IGNORE: cyclopts.App = cyclopts.App(name="ignore", help="Ignore operations.")
APP_JWT: cyclopts.App = cyclopts.App(name="jwt", help="JWT operations.")
APP_KEY: cyclopts.App = cyclopts.App(name="key", help="Key operations.")
APP_RELEASE: cyclopts.App = cyclopts.App(name="release", help="Release operations.")
APP_SSH: cyclopts.App = cyclopts.App(name="ssh", help="SSH operations.")
APP_VOTE: cyclopts.App = cyclopts.App(name="vote", help="Vote operations.")
VERSION: str = metadata.version("apache-trusted-releases")

type JSON = dict[str, Any] | list[Any] | str | int | float | bool | None


class ForceUnexpiredOpenPGPKey(pgpy.PGPKey):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __iter__(self) -> Generator[pgpy.PGPKey]:
        # Just for the type checker
        yield self

    @property
    def is_expired(self) -> bool:
        return False


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
    announce_args = models.api.ReleaseAnnounceArgs(
        project=project,
        version=version,
        revision=revision,
        email_to=mailing_list,
        subject=subject or f"[ANNOUNCE] Release {project} {version}",
        body=body or f"Release {project} {version} has been announced.",
        path_suffix=path_suffix or "",
    )
    announce = api.release_announce(announce_args)
    if not announce.success:
        show.error_and_exit("Failed to announce release.")
    print("Announcement sent.")


@APP.command(name="api", help="Call the API directly.")
def app_api(path: str, /, **kwargs: str) -> None:
    jwt_value = config.jwt_usable()
    host, verify_ssl = config.host_get()
    url = f"https://{host}/api{path}"
    # if debugging:
    #     print(url)
    #     print(kwargs)
    if "_version" in kwargs:
        # TODO: There's a bug in Cyclopts where it does not pass --version to **kwargs
        kwargs["version"] = kwargs["_version"]
        del kwargs["_version"]
    if not basic.is_json(kwargs):
        show.error_and_exit(f"Unexpected API response: {kwargs}")
    if not basic.is_json_dict(kwargs):
        show.error_and_exit(f"Unexpected API response: {kwargs}")
    json_data = asyncio.run(web.post_json(url, kwargs, jwt_value, verify_ssl))
    print(json.dumps(json_data, indent=None))


@APP_CHECK.command(name="exceptions", help="Get check exceptions for a release revision.")
def app_check_exceptions(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    checks_list = api.checks_list(project, version, revision)
    checks_display_status("exception", checks_list.checks, members=members)


@APP_CHECK.command(name="failures", help="Get check failures for a release revision.")
def app_check_failures(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    checks_list = api.checks_list(project, version, revision)
    checks_display_status("failure", checks_list.checks, members=members)


@APP_CHECK.command(name="status", help="Get check status for a release revision.")
def app_check_status(
    project: str,
    version: str,
    /,
    revision: str | None = None,
    verbose: Annotated[bool, cyclopts.Parameter(alias="-v", name="--verbose")] = False,
) -> None:
    releases_version = api.release_get(project, version)
    release = releases_version.release
    # TODO: Handle the not found case better
    if release.phase != "release_candidate_draft":
        print("Checks are not applicable for this release phase.")
        print("Checks are only performed during the draft phase.")
        return

    if revision is None:
        if release.latest_revision_number is None:
            show.error_and_exit("No revision number found.")
        if not isinstance(release.latest_revision_number, str):
            show.error_and_exit(f"Unexpected API response: {release.latest_revision_number}")
        revision = release.latest_revision_number

    checks_list = api.checks_list(project, version, revision)
    checks_display(checks_list.checks, verbose)


@APP_CHECK.command(name="wait", help="Wait for checks to be completed.")
def app_check_wait(
    project: str,
    version: str,
    /,
    revision: str | None = None,
    timeout: Annotated[float, cyclopts.Parameter(alias="-t", name="--timeout")] = 60,
    interval: Annotated[int, cyclopts.Parameter(alias="-i", name="--interval")] = 500,
) -> None:
    _host, verify_ssl = config.host_get()
    if verify_ssl is True:
        if interval < 500:
            show.error_and_exit("Interval must be at least 500ms.")
    interval_seconds = interval / 1000
    if interval_seconds > timeout:
        show.error_and_exit("Interval must be less than timeout.")
    while True:
        checks_ongoing = api.checks_ongoing(project, version, revision)
        if checks_ongoing.ongoing == 0:
            break
        time.sleep(interval_seconds)
        timeout -= interval_seconds
        if timeout <= 0:
            show.error_and_exit("Timeout waiting for checks to complete.")
    print("Checks completed.")


@APP_CHECK.command(name="warnings", help="Get check warnings for a release revision.")
def app_check_warnings(
    project: str,
    version: str,
    revision: str,
    /,
    members: Annotated[bool, cyclopts.Parameter(alias="-m", name="--members")] = False,
) -> None:
    checks_list = api.checks_list(project, version, revision)
    checks_display_status("warning", checks_list.checks, members=members)


@APP_CONFIG.command(name="file", help="Display the configuration file contents.")
def app_config_file() -> None:
    path = config.path()
    if not path.exists():
        show.error_and_exit("No configuration file found.")

    with path.open("r", encoding="utf-8") as fh:
        for chunk in fh:
            print(chunk, end="")


@APP_CONFIG.command(name="path", help="Show the configuration file path.")
def app_config_path() -> None:
    print(config.path())


@APP_DEV.command(name="delete", help="Delete a release.")
def app_dev_delete(project: str, version: str, /) -> None:
    releases_delete_args = models.api.ReleaseDeleteArgs(project=project, version=version)
    api.release_delete(releases_delete_args)
    print(f"{project}-{version}")


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
        show.error_and_exit("~/.atr-pat not found.")
    text = atr_pat_path.read_text(encoding="utf-8").removesuffix("\n")
    print(text)


@APP_DEV.command(name="pwd", help="Show the current working directory.")
def app_dev_pwd() -> None:
    print(os.getcwd())


@APP_DEV.command(name="stamp", help="Update version and exclude-newer in pyproject.toml.")
def app_dev_stamp() -> None:
    path = pathlib.Path("pyproject.toml")
    if not path.exists():
        show.error_and_exit("pyproject.toml not found.")

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
        show.warning("tests/cli_version.t not found.")
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
    draft_delete_args = models.api.ReleaseDraftDeleteArgs(project=project, version=version)
    draft_delete = api.release_draft_delete(draft_delete_args)
    print(draft_delete.success)


@APP_DISTRIBUTION.command(name="record", help="Record a distribution.")
def app_distribution_record(
    project: str,
    version: str,
    platform: str,
    distribution_owner_namespace: str | None,
    distribution_package: str,
    distribution_version: str,
    staging: bool,
    details: bool,
) -> None:
    # if not distribution_owner_namespace:
    #     distribution_owner_namespace = None
    if platform not in models.sql.DistributionPlatform.__members__:
        show.error_and_exit(f"Invalid platform: {platform}")
    platform_member = models.sql.DistributionPlatform[platform]
    distribution_record_args = models.api.DistributionRecordArgs(
        project=project,
        version=version,
        platform=platform_member,
        distribution_owner_namespace=distribution_owner_namespace,
        distribution_package=distribution_package,
        distribution_version=distribution_version,
        staging=staging,
        details=details,
    )
    distribution_record = api.distribution_record(distribution_record_args)
    if not distribution_record.success:
        show.error_and_exit("Failed to record distribution.")
    if not distribution_record.success:
        show.error_and_exit("Failed to record distribution.")
    print("Distribution recorded.")


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
        show.error_and_exit("Not a valid configuration key")

    with config.lock(write_to_disk=True) as cfg:
        present, _ = config.walk(cfg, parts, "drop")
        if not present:
            show.error_and_exit(f"Could not find {path} in the configuration file")

    print(f"Removed {path}.")


@APP_IGNORE.command(name="add", help="Add a check ignore.")
def app_ignore_add(
    committee: str,
    /,
    release: str | None = None,
    revision: str | None = None,
    checker: str | None = None,
    primary_rel_path: str | None = None,
    member_rel_path: str | None = None,
    status: models.sql.CheckResultStatusIgnore | None = None,
    message: str | None = None,
) -> None:
    args = models.api.IgnoreAddArgs(
        committee_name=committee,
        release_glob=release,
        revision_number=revision,
        checker_glob=checker,
        primary_rel_path_glob=primary_rel_path,
        member_rel_path_glob=member_rel_path,
        status=status,
        message_glob=message,
    )
    api.ignore_add(args)
    print("Check result ignored for:")
    print(f"  Committee: {committee}")
    print(f"  Release (glob): {release}")
    print(f"  Revision: {revision}")
    print(f"  Checker (glob): {checker}")
    print(f"  Primary rel path (glob): {primary_rel_path}")
    print(f"  Member rel path (glob): {member_rel_path}")
    print(f"  Status: {status}")
    print(f"  Message (glob): {message}")


@APP_IGNORE.command(name="delete", help="Delete a check ignore.")
def app_ignore_delete(
    committee: str,
    id: int,
    /,
) -> None:
    args = models.api.IgnoreDeleteArgs(committee=committee, id=id)
    api.ignore_delete(args)
    print("Check ignore deleted for:")
    print(f"  Committee: {committee}")
    print(f"  ID: {id}")


@APP_IGNORE.command(name="list", help="List check ignores.")
def app_ignore_list(
    committee: str,
    /,
) -> None:
    ignores = api.ignore_list(committee)
    for ignore in ignores.ignores:
        print(ignore.model_dump_json(indent=None))


@APP_JWT.command(name="dump", help="Show decoded JWT payload from stored config.")
def app_jwt_dump() -> None:
    jwt_value = config.jwt_get()
    if jwt_value is None:
        show.error_and_exit("No JWT stored in configuration.")

    header = jwt.get_unverified_header(jwt_value)
    if header != {"alg": "HS256", "typ": "JWT"}:
        show.error_and_exit("Invalid JWT header.")

    try:
        payload = jwt.decode(jwt_value, options={"verify_signature": False})
    except jwt.PyJWTError as e:
        show.error_and_exit(f"Failed to decode JWT: {e}")

    print(json.dumps(payload, indent=None))


@APP_JWT.command(name="info", help="Show JWT payload in human-readable form.")
def app_jwt_info() -> None:
    jwt_value, payload = config.jwt_payload()
    if jwt_value is None:
        show.error_and_exit("No JWT stored in configuration.")

    lines: list[str] = []
    for key, val in payload.items():
        if key in ("exp", "iat", "nbf"):
            val = timestamp_format(val)
        lines.append(f"{key.title()}: {val}")

    print("\n".join(lines))


@APP_JWT.command(name="refresh", help="Fetch a JWT using the stored PAT and store it in config.")
def app_jwt_refresh(asf_uid: str | None = None) -> None:
    jwt_value = config.jwt_refresh(asf_uid)
    print(jwt_value)


@APP_JWT.command(name="show", help="Show stored JWT token.")
def app_jwt_show() -> None:
    return app_show("tokens.jwt")


@APP_KEY.command(name="add", help="Add an OpenPGP key.")
def app_key_add(path: str, committees: str = "", /) -> None:
    selected_committee_names = []
    if committees:
        selected_committee_names[:] = committees.split(",")
    key = pathlib.Path(path).read_text(encoding="utf-8")
    with config.lock() as cfg:
        asf_uid = config.get(cfg, ["asf", "uid"])
    if asf_uid is None:
        show.error_and_exit("Please configure asf.uid before adding a key.")
    keys_add_args = models.api.KeyAddArgs(asfuid=asf_uid, key=key, committees=selected_committee_names)
    keys_add = api.key_add(keys_add_args)
    print(keys_add.fingerprint)


@APP_KEY.command(name="delete", help="Delete an OpenPGP key.")
def app_key_delete(fingerprint: str, /) -> None:
    keys_delete_args = models.api.KeyDeleteArgs(fingerprint=fingerprint)
    keys_delete = api.key_delete(keys_delete_args)
    print(keys_delete.success)


@APP_KEY.command(name="get", help="Get an OpenPGP key.")
def app_key_get(fingerprint: str, /) -> None:
    keys_get = api.key_get(fingerprint)
    print(keys_get.key.model_dump_json(indent=None))


@APP_KEY.command(name="upload", help="Upload a KEYS file.")
def app_key_upload(path: str, selected_committee_name: str, /) -> None:
    # selected_committee_names = []
    # if selected_committees:
    #     selected_committee_names[:] = selected_committees.split(",")
    key = pathlib.Path(path).read_text(encoding="utf-8")
    keys_upload_args = models.api.KeysUploadArgs(filetext=key, committee=selected_committee_name)
    keys_upload = api.keys_upload(keys_upload_args)
    for result in keys_upload.results:
        print(result.model_dump_json(indent=None))
    print(f"Successfully uploaded {keys_upload.success_count} keys.")
    print(f"Failed to upload {keys_upload.error_count} keys.")


@APP_KEY.command(name="user", help="List OpenPGP keys for a user.")
def app_key_user(asf_uid: str | None = None) -> None:
    if asf_uid is None:
        with config.lock() as cfg:
            asf_uid = config.get(cfg, ["asf", "uid"])
    if asf_uid is None:
        show.error_and_exit("No ASF UID provided and asf.uid not configured.")
    keys_user = api.keys_user(asf_uid)
    for key in keys_user.keys:
        print(key.model_dump_json(indent=None))


@APP.command(name="list", help="List all files within a release.")
def app_list(project: str, version: str, revision: str | None = None, /) -> None:
    releases_paths = api.release_paths(project, version, revision)
    for rel_path in releases_paths.rel_paths:
        print(rel_path)


@APP_RELEASE.command(name="info", help="Show information about a release.")
def app_release_info(project: str, version: str, /) -> None:
    releases_version = api.release_get(project, version)
    print(releases_version.release.model_dump_json(indent=None))


@APP_RELEASE.command(name="list", help="List releases for a project.")
def app_release_list(project: str, /) -> None:
    # TODO: Support showing all of a user's releases if no project is provided
    releases_project = api.project_releases(project)
    releases_display(releases_project.releases)


@APP_RELEASE.command(name="start", help="Start a release.")
def app_release_start(project: str, version: str, /) -> None:
    releases_create_args = models.api.ReleaseCreateArgs(project=project, version=version)
    releases_create = api.release_create(releases_create_args)
    print(releases_create.release.model_dump_json(indent=None))


@APP.command(name="revisions", help="List all revisions for a release.")
def app_revisions(project: str, version: str, /) -> None:
    revisions = api.release_revisions(project, version)
    for revision in revisions.revisions:
        print(revision)


@APP.command(name="rsync", help="Rsync a release.")
def app_rsync(project: str, version: str, source: str = ".", target: str = "/", /) -> None:
    import subprocess

    with config.lock() as cfg:
        asf_uid = config.get(cfg, ["asf", "uid"])
    if asf_uid is None:
        show.error_and_exit("Please configure asf.uid before uploading.")

    if not source.endswith("/"):
        source += "/"

    if target.startswith("./"):
        target = target[2:]
    elif target.startswith("/"):
        target = target[1:]
    if target and (not target.endswith("/")):
        # Must not do this if target is empty
        target += "/"

    host, _verify_ssl = config.host_get()
    if ":" in host:
        host, _port = host.split(":", 1)
    remote_target = f"{asf_uid}@{host}:/{project}/{version}/{target}"
    cmd = ["rsync", "-av", "-e", "ssh -p 2222", source, remote_target]
    subprocess.run(cmd, check=True)


@APP.command(name="set", help="Set a configuration value using dot notation.")
def app_set(path: str, value: str, /) -> None:
    parts = path.split(".")
    if not parts:
        show.error_and_exit("Not a valid configuration key.")

    with config.lock(write_to_disk=True) as cfg:
        config.set_value(cfg, path.split("."), value)

    print(f"Set {path} to {json.dumps(value, indent=None)}.")


@APP.command(name="show", help="Show a configuration value using dot notation.")
def app_show(path: str, /) -> None:
    parts = path.split(".")
    if not parts:
        show.error_and_exit("Not a valid configuration key.")

    with config.lock() as cfg:
        value = config.get(cfg, parts)

    if value is None:
        show.error_and_exit(f"Could not find {path} in the configuration file.")

    print(value)


@APP_SSH.command(name="add", help="Add an SSH key.")
def app_ssh_add(text: str, /) -> None:
    ssh_add_args = models.api.SshKeyAddArgs(text=text)
    ssh_add = api.ssh_key_add(ssh_add_args)
    print(ssh_add.fingerprint)


@APP_SSH.command(name="delete", help="Delete an SSH key.")
def app_ssh_delete(fingerprint: str, /) -> None:
    ssh_delete_args = models.api.SshKeyDeleteArgs(fingerprint=fingerprint)
    ssh_delete = api.ssh_key_delete(ssh_delete_args)
    print(ssh_delete.success)


@APP_SSH.command(name="list", help="List SSH keys.")
def app_ssh_list(asf_uid: str | None = None) -> None:
    if asf_uid is None:
        with config.lock() as cfg:
            asf_uid = config.get(cfg, ["asf", "uid"])
    if asf_uid is None:
        show.error_and_exit("No ASF UID provided and asf.uid not configured.")
    ssh_list = api.ssh_keys_list(asf_uid)
    print(ssh_list.data)


@APP.command(name="upload", help="Upload a file to a release.")
def app_upload(project: str, version: str, path: str, filepath: str, /) -> None:
    with open(filepath, "rb") as fh:
        content = fh.read()

    upload_args = models.api.ReleaseUploadArgs(
        project=project,
        version=version,
        relpath=path,
        content=base64.b64encode(content).decode("utf-8"),
    )

    upload = api.release_upload(upload_args)
    print(upload.revision.model_dump_json(indent=None))


@APP.command(name="verify", help="Verify an artifact.")
def app_verify(url: str, /, verbose: bool = False) -> None:
    def print_if_verbose(message: str) -> None:
        if verbose:
            print(message)

    if url.endswith(".asc"):
        artifact_url = url[:-4]
        signature_url = url
        print_if_verbose("You provided the signature file URL:\n")
        print_if_verbose(signature_url + "\n")
        print_if_verbose("And we will assume that the artifact file URL is here:\n")
        print_if_verbose(artifact_url)
    else:
        artifact_url = url
        signature_url = url + ".asc"
        print_if_verbose("You provided the artifact file URL:\n")
        print_if_verbose(artifact_url + "\n")
        print_if_verbose("And we will assume that the signature file URL is here:\n")
        print_if_verbose(signature_url)
    print_if_verbose("")

    print_if_verbose("We will now download the artifact and then the signature from these URLs.\n")
    artifact_data = asyncio.run(web.get_url(artifact_url, verify_ssl=False))
    signature_data = asyncio.run(web.get_url(signature_url, verify_ssl=False))
    if not signature_data:
        show.error_and_exit(f"Signature is empty: {signature_url}")
    artifact_hash = hashlib.sha3_256(artifact_data).hexdigest()
    signature_hash = hashlib.sha3_256(signature_data).hexdigest()
    print_if_verbose(f"The artifact file is {len(artifact_data):,} bytes in size, and its SHA3-256 is:\n")
    print_if_verbose(artifact_hash + "\n")
    print_if_verbose(f"The signature file is {len(signature_data):,} bytes in size, and its SHA3-256 is:\n")
    print_if_verbose(signature_hash)
    print_if_verbose("")

    artifact_file_name = artifact_url.split("/")[-1]
    signature_asc_text = signature_data.decode("utf-8", errors="ignore")
    signature_file_name = signature_url.split("/")[-1]

    print_if_verbose("To verify the signature, we need the OpenPGP signing key from the ATR.\n")
    verify_provenance_args = models.api.SignatureProvenanceArgs(
        artifact_file_name=artifact_file_name,
        artifact_sha3_256=artifact_hash,
        signature_file_name=signature_file_name,
        signature_asc_text=signature_asc_text,
        signature_sha3_256=signature_hash,
    )
    print_if_verbose("To get the key, we are going to send the following API request:\n")
    dumped_json = verify_provenance_args.model_dump()
    dumped_json["signature_asc_text"] = dumped_json["signature_asc_text"][:32] + "..."
    print_if_verbose(json.dumps(dumped_json, indent=2))
    print_if_verbose("")
    verify_provenance = api.signature_provenance(verify_provenance_args)
    print_if_verbose("The ATR found a matching OpenPGP key with the following fingerprint:\n")
    print_if_verbose(verify_provenance.fingerprint.upper() + "\n")
    print_if_verbose("This key is associated with these committees with a project containing the artifact:\n")
    for committee_with_artifact in verify_provenance.committees_with_artifact:
        print_if_verbose(f"-- {committee_with_artifact.committee} --")
        print_if_verbose(f"KEYS URL: {committee_with_artifact.keys_file_url}")
        print_if_verbose(f"SHA3-256: {committee_with_artifact.keys_file_sha3_256}")
        print_if_verbose("")

    print_if_verbose("We can now try to verify the signature using the OpenPGP key from the ATR.\n")
    print_if_verbose("Note that we ignore key expiry, so we consider expired key signatures to be valid.\n")
    verify_summary(verify_provenance, signature_data, artifact_data, verbose)


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
    api.vote_resolve(vote_resolve_args)
    print(f"Vote marked as {resolution}.")


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
    vote_start = api.vote_start(vote_start_args)
    print(vote_start.task.model_dump_json(indent=None))


@APP_VOTE.command(name="tabulate", help="Tabulate a vote.")
def app_vote_tabulate(project: str, version: str, /) -> None:
    vote_tabulate_args = models.api.VoteTabulateArgs(project=project, version=version)
    vote_tabulate = api.vote_tabulate(vote_tabulate_args)
    print(vote_tabulate.model_dump_json(indent=2))


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


@contextlib.contextmanager
def quiet() -> Generator[None]:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


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


def subcommands_register(app: cyclopts.App) -> None:
    app.command(APP_CHECK)
    app.command(APP_CONFIG)
    app.command(APP_DEV)
    app.command(APP_DISTRIBUTION)
    app.command(APP_DRAFT)
    app.command(APP_IGNORE)
    app.command(APP_JWT)
    app.command(APP_KEY)
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


def verify_summary(
    verify_provenance: models.api.SignatureProvenanceResults,
    signature_data: bytes,
    artifact_data: bytes,
    verbose: bool = False,
) -> None:
    key, _ = ForceUnexpiredOpenPGPKey.from_blob(verify_provenance.key_asc_text)
    sig = pgpy.PGPSignature.from_blob(signature_data)
    with quiet():
        verification_result = key.verify(artifact_data, sig)
    bad_signatures = sum(1 for _ in verification_result.bad_signatures)
    good_signatures = sum(1 for _ in verification_result.good_signatures)
    if bad_signatures:
        if good_signatures:
            show.error_and_exit("There was an uncertain mixture of good and bad signatures.")
        for bad_signature in verification_result.bad_signatures:
            for issue in bad_signature.issues:
                print(f"The verification package reported the following issue: {issue.name}")
        show.error_and_exit("The signature is not valid!")
    if verbose:
        print("The signature is valid! This completes the verification process.")
    else:
        print("The signature is valid!")
