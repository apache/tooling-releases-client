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

# TODO: Use transcript style script testing

from __future__ import annotations

import os
import pathlib
import re
import shlex
import shutil
import tempfile
from typing import TYPE_CHECKING, Any, Final

import aioresponses
import pytest

import atrclient.client as client
import atrclient.config as config

if TYPE_CHECKING:
    import pytest_console_scripts


REGEX_CAPTURE: Final[re.Pattern[str]] = re.compile(r"<\?([A-Za-z_]+)\?>|<.(skip).>|(.+?)")
REGEX_COMMENT: Final[re.Pattern[str]] = re.compile(r"<#.*?#>")
REGEX_USE: Final[re.Pattern[str]] = re.compile(r"<!([A-Za-z_]+)!>")


def decorator_transcript_file_paths() -> list[pathlib.Path]:
    parent = pathlib.Path(__file__).parent
    paths = list(parent.glob("*.t"))
    return paths


def test_app_checks_status_non_draft_phase(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path
) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")

    releases_url = "https://example.invalid/api/release/get/test-project/2.3.0"

    with aioresponses.aioresponses() as mock:
        mock.get(
            releases_url,
            status=200,
            payload={
                "endpoint": "/release/get",
                "release": {
                    "name": "test-project-2.3.0",
                    "project_name": "test-project",
                    "version": "2.3.0",
                    "phase": "release",
                    "created": "2024-07-04T00:00:00.000000Z",
                    "latest_revision_number": "00001",
                    "package_managers": [],
                    "sboms": [],
                    "votes": [],
                    "vote_manual": False,
                },
            },
        )

        client.app_check_status("test-project", "2.3.0", "00001")

        captured = capsys.readouterr()
        assert "Checks are not applicable for this release phase." in captured.out
        assert "Checks are only performed during the draft phase." in captured.out


def test_app_checks_status_verbose(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")

    release_url = "https://example.invalid/api/release/get/test-project/2.3.1"
    checks_url = "https://example.invalid/api/checks/list/test-project/2.3.1/00003"

    release_payload = {
        "endpoint": "/release/get",
        "release": {
            "name": "test-project-2.3.1",
            "project_name": "test-project",
            "version": "2.3.1",
            "phase": "release_candidate_draft",
            "created": "2025-01-01T00:00:00.000000Z",
            "latest_revision_number": "00003",
            "package_managers": [],
            "sboms": [],
            "votes": [],
            "vote_manual": False,
        },
    }

    checks_payload = {
        "endpoint": "/checks/list",
        "checks_revision": "00003",
        "current_phase": "release_candidate_draft",
        "checks": [
            {
                "release_name": "test-project-2.3.1",
                "revision_number": "00003",
                "created": "2025-01-01T00:00:00Z",
                "status": "blocker",
                "checker": "test_checker1",
                "primary_rel_path": "file1.txt",
                "member_rel_path": None,
                "message": "Test blocker 1",
                "data": None,
            },
            {
                "release_name": "test-project-2.3.1",
                "revision_number": "00003",
                "created": "2025-01-01T00:00:00Z",
                "status": "blocker",
                "checker": "test_checker2",
                "primary_rel_path": "file2.txt",
                "member_rel_path": "inner.txt",
                "message": "Test blocker 2",
                "data": None,
            },
            {
                "release_name": "test-project-2.3.1",
                "revision_number": "00003",
                "created": "2025-01-01T00:00:00Z",
                "status": "note",
                "checker": "test_checker3",
                "primary_rel_path": "file3.txt",
                "member_rel_path": None,
                "message": "Test note",
                "data": None,
            },
        ],
    }

    with aioresponses.aioresponses() as mock:
        mock.get(release_url, status=200, payload=release_payload)
        mock.get(checks_url, status=200, payload=checks_payload)

        client.app_check_status("test-project", "2.3.1", "00003", verbose=True)

        captured = capsys.readouterr()
        assert "(top-level" in captured.out
        assert "blocker: 2 (top-level 1, inner 1)" in captured.out
        assert "  note: 1\n" in captured.out
        assert "test_checker1 → file1.txt : Test blocker 1" in captured.out


def test_app_check_bucket_commands_list_results(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path
) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")

    checks_url = "https://example.invalid/api/checks/list/test-project/2.3.1/00003"

    def check(status: str, checker: str, path: str, message: str) -> dict[str, Any]:
        return {
            "release_name": "test-project-2.3.1",
            "revision_number": "00003",
            "created": "2025-01-01T00:00:00Z",
            "status": status,
            "checker": checker,
            "primary_rel_path": path,
            "member_rel_path": None,
            "message": message,
            "data": None,
        }

    checks_payload = {
        "endpoint": "/checks/list",
        "checks_revision": "00003",
        "current_phase": "release_candidate_draft",
        "checks": [
            check("blocker", "rat", "blocker.txt", "A blocking problem"),
            check("concern", "rat", "concern.txt", "A concern"),
            check("suggestion", "rat", "suggestion.txt", "A suggestion"),
            check("note", "rat", "note.txt", "Just a note"),
        ],
    }

    cases = [
        (client.app_check_blockers, "blocker.txt", "A blocking problem"),
        (client.app_check_concerns, "concern.txt", "A concern"),
        (client.app_check_suggestions, "suggestion.txt", "A suggestion"),
        (client.app_check_notes, "note.txt", "Just a note"),
    ]
    for command, expected_path, expected_message in cases:
        with aioresponses.aioresponses() as mock:
            mock.get(checks_url, status=200, payload=checks_payload)
            command("test-project", "2.3.1", "00003")
        out = capsys.readouterr().out
        assert expected_path in out
        assert expected_message in out
        other_messages = [m for _, _, m in cases if m != expected_message]
        for other in other_messages:
            assert other not in out


def test_app_check_concerns_group_summary(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")

    checks_url = "https://example.invalid/api/checks/list/test-project/2.3.1/00003"

    checks = []
    for checker, member in [
        ("atr.tasks.checks.license.headers", None),
        ("atr.tasks.checks.license.headers", "inner.sh"),
        ("atr.tasks.checks.paths", None),
    ]:
        checks.append(
            {
                "release_name": "test-project-2.3.1",
                "revision_number": "00003",
                "created": "2025-01-01T00:00:00Z",
                "status": "concern",
                "checker": checker,
                "primary_rel_path": "a.tar.gz",
                "member_rel_path": member,
                "message": "A concern",
                "data": None,
            }
        )
    checks_payload = {
        "endpoint": "/checks/list",
        "checks_revision": "00003",
        "current_phase": "release_candidate_draft",
        "checks": checks,
    }

    with aioresponses.aioresponses() as mock:
        mock.get(checks_url, status=200, payload=checks_payload)
        client.app_check_concerns("test-project", "2.3.1", "00003")
    out = capsys.readouterr().out
    assert "Concern groups (keys for vote start --concerns-noted):" in out
    assert " - atr.tasks.checks.license.headers (2)" in out
    assert " - atr.tasks.checks.paths (1)" in out


def test_app_release_list_not_found(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")

    releases_url = "https://example.invalid/api/project/releases/nonexistent-project"

    with aioresponses.aioresponses() as mock:
        mock.get(releases_url, status=404, body="Not Found")

        with pytest.raises(SystemExit):
            client.app_release_list("nonexistent-project")


def test_app_release_list_success(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")

    releases_url = "https://example.invalid/api/project/releases/test-project"

    payload = {
        "endpoint": "/project/releases",
        "releases": [
            {
                "name": "test-project-2.3.1",
                "project_name": "test-project",
                "version": "2.3.1",
                "phase": "release_candidate_draft",
                "created": "2025-01-01T00:00:00.000000Z",
                "latest_revision_number": "00003",
                "package_managers": [],
                "sboms": [],
                "votes": [],
                "vote_manual": False,
            },
            {
                "name": "test-project-2.3.0",
                "project_name": "test-project",
                "version": "2.3.0",
                "phase": "release",
                "created": "2024-07-04T00:00:00.000000Z",
                "latest_revision_number": "00001",
                "package_managers": [],
                "sboms": [],
                "votes": [],
                "vote_manual": False,
            },
        ],
    }

    with aioresponses.aioresponses() as mock:
        mock.get(releases_url, status=200, payload=payload)

        client.app_release_list("test-project")

        captured = capsys.readouterr()
        assert "Total releases: 2" in captured.out
        assert "2.3.1" in captured.out
        assert "2.3.0" in captured.out


def test_app_distribution_list_success(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")

    distributions_url = "https://example.invalid/api/distribution/list/test-project/2.3.1"

    payload = {
        "endpoint": "/distribution/list",
        "distributions": [
            {
                "platform": "ARTIFACT_HUB",
                "owner_namespace": "acme",
                "package": "widget",
                "version": "0.0.1",
                "staging": False,
                "pending": True,
                "upload_date": "2026-06-15T12:00:00+00:00",
                "api_url": "https://api.example/x",
                "web_url": "https://web.example/x",
            },
            {
                "platform": "NPM",
                "owner_namespace": "",
                "package": "thing",
                "version": "1.2.3",
                "staging": True,
                "pending": False,
            },
        ],
    }

    with aioresponses.aioresponses() as mock:
        mock.get(distributions_url, status=200, payload=payload)

        client.app_distribution_list("test-project", "2.3.1")

        captured = capsys.readouterr()
        assert "ARTIFACT_HUB acme/widget@0.0.1 (pending)" in captured.out
        assert "NPM -/thing@1.2.3 (staging)" in captured.out


def test_app_distribution_list_empty(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")
    capsys.readouterr()

    distributions_url = "https://example.invalid/api/distribution/list/test-project/2.3.1"

    with aioresponses.aioresponses() as mock:
        mock.get(distributions_url, status=200, payload={"endpoint": "/distribution/list", "distributions": []})

        client.app_distribution_list("test-project", "2.3.1")

        assert capsys.readouterr().out == ""


def test_app_set_show(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_show("atr.host")
    assert capsys.readouterr().out == 'Set atr.host to "example.invalid".\nexample.invalid\n'


def test_cli_version(script_runner: pytest_console_scripts.ScriptRunner) -> None:
    result = script_runner.run(["atr", "--version"])
    assert result.returncode == 0
    assert result.stdout == f"{client.VERSION}\n"
    assert result.stderr == ""


@pytest.mark.parametrize("transcript_path", decorator_transcript_file_paths(), ids=lambda p: p.name)
def test_cli_transcripts(
    transcript_path: pathlib.Path,
    script_runner: pytest_console_scripts.ScriptRunner,
    fixture_config_env: pathlib.Path,
) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        files_dir = transcript_path.parent / "files"
        for file_path in files_dir.iterdir():
            shutil.copy(file_path, tmpdir)
        return transcript_capture(transcript_path, script_runner, fixture_config_env)


def test_config_set_get_roundtrip() -> None:
    cfg: dict[str, Any] = {}
    config.set_value(cfg, ["abc", "pqr"], 123)
    assert config.get(cfg, ["abc", "pqr"]) == 123


def test_config_walk_drop() -> None:
    cfg: dict[str, Any] = {"a": {"b": 1}}
    changed, _ = config.walk(cfg, ["a", "b"], "drop")
    assert changed is True
    assert cfg == {}


def test_config_write_delete(fixture_config_env: pathlib.Path) -> None:
    config.write({"atr": {"host": "example.invalid"}})
    config_path_obj = config.path()
    assert config_path_obj.exists() is True
    cfg = {}
    config.write(cfg)
    assert config_path_obj.exists() is False


def test_config_write_empty_dict_filter(fixture_config_env: pathlib.Path) -> None:
    config.write({"atr": {}, "asf": {"uid": ""}})
    cfg = config.read()
    assert "atr" not in cfg
    assert config.get(cfg, ["asf", "uid"]) == ""


def test_timestamp_format_epoch() -> None:
    assert client.timestamp_format(0) == "01 Jan 1970 at 00:00:00 UTC"


def test_timestamp_format_none_and_bad() -> None:
    assert client.timestamp_format(None) is None
    assert client.timestamp_format("bad") == "bad"


def transcript_capture(
    transcript_path: pathlib.Path,
    script_runner: pytest_console_scripts.ScriptRunner,
    transcript_config_path: pathlib.Path,
) -> None:
    captures = {}
    actual_output = []

    env = os.environ.copy()

    env["ATR_CLIENT_CONFIG_PATH"] = str(transcript_config_path)
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "<.exit.>":
                return
            if captures:
                line = REGEX_USE.sub(lambda m: captures[m.group(1)], line)
            line = REGEX_COMMENT.sub("", line)
            if line.startswith("$ ") or line.startswith("! ") or line.startswith("* "):
                actual_output = transcript_execute(actual_output, line, script_runner, env)
            elif line == "<.etc.>":
                actual_output[:] = []
            elif actual_output:
                captures, actual_output = transcript_match(captures, actual_output, line)
            elif line:
                pytest.fail(f"Unexpected line: {line!r}")
        assert not actual_output


def transcript_execute(
    actual_output: list[str],
    line: str,
    script_runner: pytest_console_scripts.ScriptRunner,
    env: dict[str, str],
) -> list[str]:
    match line[:1]:
        case "$":
            expected_code = 0
        case "!":
            expected_code = 1
        case "*":
            expected_code = None
        case _:
            pytest.fail(f"Unknown line prefix: {line[:1]!r}")
    command = line[2:]
    if not command.startswith("atr"):
        pytest.fail(f"Command does not start with 'atr': {command}")
    print(f"Running: {command}")
    result = script_runner.run(shlex.split(command), env=env)
    if expected_code is not None:
        assert result.returncode == expected_code, f"Command {command!r} returned {result.returncode}"
    actual_output[:] = result.stdout.splitlines()
    if result.stderr:
        actual_output.append("<.stderr.>")
        actual_output.extend(result.stderr.splitlines())
    return actual_output


def transcript_match(captures: dict[str, str], actual_output: list[str], line: str) -> tuple[dict[str, str], list[str]]:
    actual_output_line = actual_output.pop(0)

    # Replace captures with (?P<name>.*?)
    # Can't lift this, because it uses use_regex
    use_regex = False

    def substitute(m: re.Match[str]) -> str:
        nonlocal use_regex
        if m.group(1):
            use_regex = True
            return f"(?P<{m.group(1)}>.*?)"
        if m.group(2) == "skip":
            use_regex = True
            return "(.*?)"
        return re.escape(m.group(3))

    line_pattern = r"^" + REGEX_CAPTURE.sub(substitute, line) + r"$"
    if use_regex:
        success = re.match(line_pattern, actual_output_line)
        if success:
            captures.update(success.groupdict())
    else:
        success = actual_output_line == line
    if not success:
        # TODO: Improve this
        got = f"{actual_output_line!r}"
        if actual_output:
            got += f", {actual_output[:10]}"
            if len(actual_output) > 10:
                got += "..."
        pytest.fail(f"Expected {line!r} but got {got}")
    return captures, actual_output
