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

import base64
import json
import os
import pathlib
import re
import shlex
import shutil
import tempfile
import time
import types
from typing import TYPE_CHECKING, Any, Final

import aioresponses
import openpgp
import pytest

import atrclient.client as client
import atrclient.config as config
import atrclient.models as models
import atrclient.sign as sign

if TYPE_CHECKING:
    import pytest_console_scripts


CERTIFIED_SECRET_KEY_ASC: Final[str] = """\
-----BEGIN PGP PRIVATE KEY BLOCK-----

lFgEal52nhYJKwYBBAHaRw8BAQdAkkyLnkBjDoWMkWAOZgW/ggtUPB5EYQcFOsnA
hHDuvGEAAP9iXlQwqx0sDxCiaSu8rWwHeKIEUqbGTfiJoMMh/OhhJQ8AtB1BbGlj
ZSA8YWxpY2VAZXhhbXBsZS5pbnZhbGlkPoiQBBMWCAA4FiEEdjj6xEQPMWWn0AbX
uzSFmcgEU/0FAmpedp4CGwMFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AACgkQuzSF
mcgEU/0I7gD/X8+cr1OcDd4aq4F1Fh+Vjis2wLDeUh65ozvbywaeTVsBAKrikfA/
qP2PaDurpAjx+CGMgHxtnWbiol9CvfXZmo4EiHQEERYIAB0WIQS3KMiD+CtJ50tI
5iSMOJ4FbDCjtwUCal52ngAKCRCMOJ4FbDCjtwPPAQDjs0Ptl7XjVDAyWTX5Im5L
7coufi7tb/mG9llbfp6chgD4r/jDimQNcN181fTDF5d04fca+BxTPDlScYDI8s8P
AA==
=XTpr
-----END PGP PRIVATE KEY BLOCK-----
"""

DUMMY_PRIMARY_SECRET_KEY_ASC: Final[str] = """\
-----BEGIN PGP PRIVATE KEY BLOCK-----

lDsEal5umhYJKwYBBAHaRw8BAQdAF5a2S+aOa7/sm1lhY0FOVSJ4TjQqXm9P7KDi
dYDlDG//AGUAR05VAbQXRkQgPGZkQGV4YW1wbGUuaW52YWxpZD6IkAQTFggAOBYh
BMYv9i9tw9g1xSUzTiXecOxBJcJkBQJqXm6aAhsDBQsJCAcCBhUKCQgLAgQWAgMB
Ah4BAheAAAoJECXecOxBJcJk2y0BAObde4WvVaYeJm6bixj2s5dowpoZUb3ToYjw
hFjKrnTeAP0WdVS7VVb6qj4yzq8aXt1AzPB5eRw2E0GxBe+Ec54dBpxdBGpebpoS
CisGAQQBl1UBBQEBB0AcSfuYUVcjmZajYSBT6AcSqOIoN3r1HFNKDW8KSl3cMAMB
CAcAAP94NDF2qJMMpmXhcha9vyxZylBuReaZhPQyNxyFc+sluBAXiHgEGBYIACAW
IQTGL/YvbcPYNcUlM04l3nDsQSXCZAUCal5umgIbDAAKCRAl3nDsQSXCZInWAQDc
kAdZj4IXUa+30atAjSfMK81+ke1XSbr1eem2OzTOMAD7Btg0rRAMkdcXQI2yDJd3
KrEwHstx97v6jH998XgUGgU=
=MgWQ
-----END PGP PRIVATE KEY BLOCK-----
"""

EXPIRED_PRIMARY_SECRET_KEY_ASC: Final[str] = """\
-----BEGIN PGP PRIVATE KEY BLOCK-----

lFgEal5mOhYJKwYBBAHaRw8BAQdAHMf234eTQDt5MZoxwkodFKpxI6mZSlplWZxt
30WD46AAAQDumEWie6PcRjc++M6OLJjwh/17TckxANk/mBiZg+W9HBETtClFeHBp
cmVkIFByaW1hcnkgPGV4cHByaW1AZXhhbXBsZS5pbnZhbGlkPoiWBBMWCAA+FiEE
DPkLRMVwc4/nZooo/tLW2VJVHXsFAmpeZjoCGwEFCQAAAAEFCwkIBwIGFQoJCAsC
BBYCAwECHgECF4AACgkQ/tLW2VJVHXufMwEA5WwbOWYPAMSBYvB53JEdUrYsqmIk
6h7x3XPiRSi62xYBAKqhnAK3gCWJcM7wZasVG3T4RwLDtL48N7vLyMN5opIDnFgE
al5mOhYJKwYBBAHaRw8BAQdAJlNciJRHYs22Uw5/g8+9EBpYQbY9mxU+1wZ5bZcI
qrMAAP9KAb0pddNBKhVDAGGxePZLCLNTMzFS0C8ntng3HRKwVQyJiO8EGBYIACAW
IQQM+QtExXBzj+dmiij+0tbZUlUdewUCal5mOgIbAgCBCRD+0tbZUlUde3YgBBkW
CAAdFiEEnWrHDsQl8472wz2KigISX+VECOsFAmpeZjoACgkQigISX+VECOuG6AEA
7gGdZVbpK0RnL34fV+WHZ3yzI33DmkHQZcjPfmiTed8BANQ1CDFyhSqonazlfNxL
waMPM6zJwdGtgMkY47hViI8G1usA/R79INPTrCjQXlrsoSjhMLGsr4ARVsNZW3pL
ecRF1e4jAP40el4/GJbSc0gwWfYAWbb3BE4yCE10rHQBY4D54ndMCg==
=e1Li
-----END PGP PRIVATE KEY BLOCK-----
"""

EXPIRED_SUBKEY_SECRET_KEY_ASC: Final[str] = """\
-----BEGIN PGP PRIVATE KEY BLOCK-----

lFgEal5mOhYJKwYBBAHaRw8BAQdAf4dBOvR5O8RB6lcaqGOEbb9aPkfN2VurCUc1
N1Te1A4AAQDeo+xFVCGr99W/XgJwE0Kileo2m5xDCU7/BTeUvxRz2A+YtCdFeHBp
cmVkIFN1YmtleSA8ZXhwc3ViQGV4YW1wbGUuaW52YWxpZD6IkAQTFggAOBYhBKv5
FOypNmunfJ9yPuSuK79fYsd3BQJqXmY6AhsBBQsJCAcCBhUKCQgLAgQWAgMBAh4B
AheAAAoJEOSuK79fYsd3AX8A/jQ1bt0sgD5ZHVIEuyrfM0COrcCodHCODBkVlJmQ
nfnUAP9clEuFA0i1UZHw9EfplE9lhGokm/CJsZ1kha44qDU8A5xYBGpeZjoWCSsG
AQQB2kcPAQEHQJu+Gb+blzPd7QNuva4McunlmPXPqTSTN65j9FY0N4fSAAD/Yj2s
UwDKFQWiM73XkFCChlbKRqBzC5Sy5NANfgMcHu8PB4j1BBgWCAAmFiEEq/kU7Kk2
a6d8n3I+5K4rv19ix3cFAmpeZjoCGwIFCQAAAAEAgQkQ5K4rv19ix3d2IAQZFggA
HRYhBMHOXgBI+zwsDhwJ9spD+1SUuTqbBQJqXmY6AAoJEMpD+1SUuTqbFckBAMAG
5UyadtXZQmt/uEs/+dfFHhQPm4Dh3xA/z1jkYWabAQD14c62mz+GMEq2oNtyr1Of
ahi0v4AqMjnQ6X6I+C5lBr1MAQCOj3exuuRsHl65gq2zk/Te6Mof3ao7YCUm7n7p
oNN5UgD7By/sRoo0u9VDkQgUEvFj+GoL2QJ0s2PrR6IWwtnKJAQ=
=iXpF
-----END PGP PRIVATE KEY BLOCK-----
"""

REVOKED_PRIMARY_UID_SECRET_KEY_ASC: Final[str] = """\
-----BEGIN PGP PRIVATE KEY BLOCK-----

lFgEal57BBYJKwYBBAHaRw8BAQdATc1jLyFqpUYCaoqbC8xo0ndcHd3mQIyIkpz4
G1Z/eYsAAPwOsmg/OyG5oFb9m8KP+0AkEaIHZTQ2+2FEVyVggJsYiA52tB1Qcmlt
ZSA8cHJpbWVAZXhhbXBsZS5pbnZhbGlkPoh4BDAWCAAgFiEE5xtcHLwTVrZEl01q
scciku2LdwoFAmpeewYCHSAACgkQscciku2LdwpsoAEA3dTlkvqJtkTv75MQky+a
drBgwGCuUl+ReEyrdUNXGtMA/iVpsA+Qqo7QhsMwzJ2WFSWAgY1hFs25lW67Bpf+
aEQMiJMEExYIADsCGwMFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AWIQTnG1wcvBNW
tkSXTWqxxyKS7Yt3CgUCal57BQIZAQAKCRCxxyKS7Yt3Cn/hAP9JDI5LkpszUr4F
hP00fzn8YqdBumZ+pmu2Qh5E4A2wPwEAqQUoTKpx1tQfuvJPrr3eN9juDvt2O2Bp
/YBn1064VgS0H1NlY29uZCA8c2Vjb25kQGV4YW1wbGUuaW52YWxpZD6IkAQTFggA
OBYhBOcbXBy8E1a2RJdNarHHIpLti3cKBQJqXnsEAhsDBQsJCAcCBhUKCQgLAgQW
AgMBAh4BAheAAAoJELHHIpLti3cKl0oA/2sqrnXuiZXkRJzyjSkOLmjxtRdW8jzU
mK9k50aR8YhPAQCOdowxbu7q8e2DKYnnuh6Zg/1A8FnedW391g+uxf+CDA==
=O3vw
-----END PGP PRIVATE KEY BLOCK-----
"""

REVOKED_UID_SECRET_KEY_ASC: Final[str] = """\
-----BEGIN PGP PRIVATE KEY BLOCK-----

lFgEal52nhYJKwYBBAHaRw8BAQdAkkyLnkBjDoWMkWAOZgW/ggtUPB5EYQcFOsnA
hHDuvGEAAP9iXlQwqx0sDxCiaSu8rWwHeKIEUqbGTfiJoMMh/OhhJQ8AtB1BbGlj
ZSA8YWxpY2VAZXhhbXBsZS5pbnZhbGlkPoh4BDAWCAAgFiEEdjj6xEQPMWWn0AbX
uzSFmcgEU/0FAmpedp8CHSAACgkQuzSFmcgEU/2BRwEAuOHOq9mjGVcKrYVZt8wT
wqhbuMer7k0cHSBybIJLZTwBAKyS2P6CEC2d8O/3hw0pyGZGv+XOQWeiCv5t3qwC
8uEAiJAEExYIADgWIQR2OPrERA8xZafQBte7NIWZyART/QUCal52ngIbAwULCQgH
AgYVCgkICwIEFgIDAQIeAQIXgAAKCRC7NIWZyART/QjuAP9fz5yvU5wN3hqrgXUW
H5WOKzbAsN5SHrmjO9vLBp5NWwEAquKR8D+o/Y9oO6ukCPH4IYyAfG2dZuKiX0K9
9dmajgSIdAQRFggAHRYhBLcoyIP4K0nnS0jmJIw4ngVsMKO3BQJqXnaeAAoJEIw4
ngVsMKO3A88BAOOzQ+2XteNUMDJZNfkibkvtyi5+Lu1v+Yb2WVt+npyGAPiv+MOK
ZA1w3XzV9MMXl3Th9xr4HFM8OVJxgMjyzw8AtCJBbGljZSBUd28gPGFsaWNlMkBl
eGFtcGxlLmludmFsaWQ+iJAEExYIADgWIQR2OPrERA8xZafQBte7NIWZyART/QUC
al52ngIbAwULCQgHAgYVCgkICwIEFgIDAQIeAQIXgAAKCRC7NIWZyART/TgPAP9b
deb72kiY7T2RChhU+zzpPtmeUNpK1bqZ+lfaFuKA6QEA4oOo/eiK0j7aHYsxTDz8
wzzaeijzmkorgOs2bIVmRA0=
=sWcV
-----END PGP PRIVATE KEY BLOCK-----
"""

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


def test_app_announce_serializes_template_default_and_bodies(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    config.write(
        {
            "atr": {"host": "example.invalid"},
            "output": {"json": True},
            "tokens": {"jwt": "dummy_jwt_token"},
        }
    )
    announce_url = "https://example.invalid/api/release/announce"
    captured_requests: list[dict[str, Any]] = []
    response_payload = {"endpoint": "/release/announce", "success": True}

    def capture_request(_url: Any, **kwargs: Any) -> aioresponses.CallbackResult:
        captured_requests.append(kwargs["json"])
        return aioresponses.CallbackResult(status=201, payload=response_payload)

    body_path = tmp_path / "announce-body.txt"
    body_path.write_text("Announcement body from file\n", encoding="utf-8")

    with aioresponses.aioresponses() as mock:
        mock.post(announce_url, callback=capture_request)
        mock.post(announce_url, callback=capture_request)
        mock.post(announce_url, callback=capture_request)
        client.app_announce("test-project", "2.3.1", mailing_list="announce@example.apache.org")
        default_record = json.loads(capsys.readouterr().out)
        client.app_announce(
            "test-project",
            "2.3.1",
            mailing_list="announce@example.apache.org",
            body="Custom announcement body",
        )
        custom_record = json.loads(capsys.readouterr().out)
        client.app_announce(
            "test-project",
            "2.3.1",
            mailing_list="announce@example.apache.org",
            body_file=str(body_path),
        )
        file_record = json.loads(capsys.readouterr().out)

    assert captured_requests[0]["body"] is None
    assert default_record["body"] is None
    assert default_record["body_rendered_by_server"] is True
    assert captured_requests[1]["body"] == "Custom announcement body"
    assert custom_record["body"] == "Custom announcement body"
    assert "body_rendered_by_server" not in custom_record
    assert captured_requests[2]["body"] == "Announcement body from file\n"
    assert file_record["body"] == "Announcement body from file\n"
    assert "body_rendered_by_server" not in file_record


def test_app_announce_rejects_body_and_body_file(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        client.app_announce(
            "test-project",
            "2.3.1",
            mailing_list="announce@example.apache.org",
            body="Literal body",
            body_file="body.txt",
        )

    assert capsys.readouterr().err == "atr: error: Cannot use both --body and --body-file.\n"


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
            check("exception", "rat", "exception.txt", "An exception"),
            check("suggestion", "rat", "suggestion.txt", "A suggestion"),
            check("note", "rat", "note.txt", "Just a note"),
        ],
    }

    cases = [
        (client.app_check_blockers, "blocker.txt", "A blocking problem"),
        (client.app_check_concerns, "concern.txt", "A concern"),
        (client.app_check_exceptions, "exception.txt", "An exception"),
        (client.app_check_suggestions, "suggestion.txt", "A suggestion"),
        (client.app_check_notes, "note.txt", "Just a note"),
    ]
    for command, expected_path, expected_message in cases:
        for revision, suffix in [(None, ""), ("00003", "/00003")]:
            checks_url = f"https://example.invalid/api/checks/list/test-project/2.3.1{suffix}"
            with aioresponses.aioresponses() as mock:
                mock.get(checks_url, status=200, payload=checks_payload)
                if revision is None:
                    command("test-project", "2.3.1")
                else:
                    command("test-project", "2.3.1", revision)
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


def test_app_check_bucket_commands_acknowledge_no_matching_results(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path
) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")
    capsys.readouterr()

    checks_url = "https://example.invalid/api/checks/list/test-project/2.3.1/00003"
    cases = [
        (client.app_check_blockers, "blocker", "note"),
        (client.app_check_concerns, "concern", "note"),
        (client.app_check_exceptions, "exception", "note"),
        (client.app_check_notes, "note", "suggestion"),
        (client.app_check_suggestions, "suggestion", "note"),
    ]

    for command, requested_status, other_status in cases:
        checks_payload = {
            "endpoint": "/checks/list",
            "checks_revision": "00003",
            "current_phase": "release_candidate_draft",
            "checks": [
                {
                    "release_name": "test-project-2.3.1",
                    "revision_number": "00003",
                    "created": "2025-01-01T00:00:00Z",
                    "status": other_status,
                    "checker": "rat",
                    "primary_rel_path": "other.txt",
                    "member_rel_path": None,
                    "message": "A different result",
                    "data": None,
                }
            ],
        }
        with aioresponses.aioresponses() as mock:
            mock.get(checks_url, status=200, payload=checks_payload)
            command("test-project", "2.3.1", "00003")

        out = capsys.readouterr().out
        assert out == f"No {requested_status} check results found for revision 00003.\n"


def test_app_check_concerns_reports_no_check_results(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path
) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")
    capsys.readouterr()

    checks_url = "https://example.invalid/api/checks/list/test-project/2.3.1/00003"
    checks_payload = {
        "endpoint": "/checks/list",
        "checks_revision": "00003",
        "current_phase": "release_candidate_draft",
        "checks": [],
    }
    with aioresponses.aioresponses() as mock:
        mock.get(checks_url, status=200, payload=checks_payload)
        client.app_check_concerns("test-project", "2.3.1", "00003")

    assert capsys.readouterr().out == "No check results found for revision 00003.\n"


def test_app_check_concerns_reports_hidden_member_results(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path
) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")

    checks_url = "https://example.invalid/api/checks/list/test-project/2.3.1/00003"
    checks_payload = {
        "endpoint": "/checks/list",
        "checks_revision": "00003",
        "current_phase": "release_candidate_draft",
        "checks": [
            {
                "release_name": "test-project-2.3.1",
                "revision_number": "00003",
                "created": "2025-01-01T00:00:00Z",
                "status": "concern",
                "checker": "atr.tasks.checks.rat.check",
                "primary_rel_path": "source.tar.gz",
                "member_rel_path": "src/example.py",
                "message": "A member concern",
                "data": None,
            }
        ],
    }
    with aioresponses.aioresponses() as mock:
        mock.get(checks_url, status=200, payload=checks_payload)
        client.app_check_concerns("test-project", "2.3.1", "00003")

    out = capsys.readouterr().out
    assert "No visible concern check results found for revision 00003." in out
    assert "1 archive-member check result hidden; use --members to show them." in out
    assert "Concern groups (keys for vote start --concerns-noted):" in out


def test_app_check_concerns_displays_release_level_results(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path
) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")

    checks_url = "https://example.invalid/api/checks/list/test-project/2.3.1/00003"

    def concern(path: str | None, message: str) -> dict[str, Any]:
        return {
            "release_name": "test-project-2.3.1",
            "revision_number": "00003",
            "created": "2025-01-01T00:00:00Z",
            "status": "concern",
            "checker": "atr.tasks.checks.rat.check",
            "primary_rel_path": path,
            "member_rel_path": None,
            "message": message,
            "data": None,
        }

    checks_payload = {
        "endpoint": "/checks/list",
        "checks_revision": "00003",
        "current_phase": "release_candidate_draft",
        "checks": [concern(None, "A release concern"), concern("source.tar.gz", "A file concern")],
    }
    with aioresponses.aioresponses() as mock:
        mock.get(checks_url, status=200, payload=checks_payload)
        client.app_check_concerns("test-project", "2.3.1", "00003")

    out = capsys.readouterr().out
    assert "(release)\n - A release concern (rat.check)" in out
    assert "source.tar.gz\n - A file concern (rat.check)" in out


def test_app_download_writes_file(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    config.write({"atr": {"host": "example.invalid"}})
    download_url = "https://example.invalid/download/path/test-project/2.3.0/artifact.tar.gz"

    with aioresponses.aioresponses() as mock:
        mock.get(download_url, status=200, body=b"artifact bytes", content_type="application/octet-stream")
        client.app_download("test-project", "2.3.0", "artifact.tar.gz", str(tmp_path))

    saved = tmp_path / "artifact.tar.gz"
    assert saved.read_bytes() == b"artifact bytes"
    assert str(saved) in capsys.readouterr().out


def test_app_download_refuses_existing_target(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    config.write({"atr": {"host": "example.invalid"}})
    existing = tmp_path / "artifact.tar.gz"
    existing.write_bytes(b"already here")

    with pytest.raises(SystemExit):
        client.app_download("test-project", "2.3.0", "artifact.tar.gz", str(tmp_path))

    assert existing.read_bytes() == b"already here"


def test_app_download_rejects_redirect(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    config.write({"atr": {"host": "example.invalid"}})
    download_url = "https://example.invalid/download/path/test-project/2.3.0/missing.tar.gz"

    with aioresponses.aioresponses() as mock:
        mock.get(download_url, status=302, headers={"Location": "https://example.invalid/"})
        with pytest.raises(SystemExit):
            client.app_download("test-project", "2.3.0", "missing.tar.gz", str(tmp_path))

    assert not (tmp_path / "missing.tar.gz").exists()


def test_app_download_rejects_non_file_response(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    config.write({"atr": {"host": "example.invalid"}})
    download_url = "https://example.invalid/download/path/test-project/2.3.0/somedir"

    with aioresponses.aioresponses() as mock:
        mock.get(download_url, status=200, body=b"<html>listing</html>", content_type="text/html")
        with pytest.raises(SystemExit):
            client.app_download("test-project", "2.3.0", "somedir", str(tmp_path))

    assert not (tmp_path / "somedir").exists()


def test_app_release_list_not_found(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("atr.host", "example.invalid")

    releases_url = "https://example.invalid/api/project/releases/nonexistent-project"

    with aioresponses.aioresponses() as mock:
        mock.get(releases_url, status=404, body="Not Found")

        with pytest.raises(SystemExit):
            client.app_release_list("nonexistent-project")


def test_app_sbom_generate_wait_polls_until_completed(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path
) -> None:
    config.write(
        {
            "atr": {"host": "example.invalid"},
            "tokens": {"jwt": "dummy_jwt_token"},
        }
    )
    generate_url = "https://example.invalid/api/sbom/generate"
    task_url = "https://example.invalid/api/task/get/42"
    queued_task = {
        "id": 42,
        "task_type": "sbom_generate",
        "task_args": {},
        "asf_uid": "test_asf_uid",
        "status": "queued",
    }
    completed_task = dict(queued_task)
    completed_task["status"] = "completed"
    completed_task["result"] = {
        "kind": "sbom_generate",
        "path": "artifact.tar.gz.cdx.json",
        "bom_version": 2,
        "revision_number": "00002",
    }

    with aioresponses.aioresponses() as mock:
        mock.post(generate_url, status=202, payload={"endpoint": "/sbom/generate", "task": queued_task})
        mock.get(task_url, status=200, payload={"endpoint": "/task/get", "task": completed_task})
        client.app_sbom_generate("test-project", "2.3.0", "artifact.tar.gz", wait=True)

    record = json.loads(capsys.readouterr().out)
    assert record["status"] == "completed"
    assert record["result"]["revision_number"] == "00002"


def test_app_sign_default_signs_locally(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    key = _ed25519_key()
    key_path = tmp_path / "signing-key.asc"
    key_path.write_text(key.to_armored(), encoding="utf-8")
    config.write({"atr": {"host": "example.invalid"}})
    download_url = "https://example.invalid/download/path/test-project/2.3.0/artifact.tar.gz.cdx.json"

    with aioresponses.aioresponses() as mock:
        mock.get(download_url, status=200, body=b"sbom bytes", content_type="application/octet-stream")
        client.app_sign("test-project", "2.3.0", "artifact.tar.gz.cdx.json", str(tmp_path), key=str(key_path))

    asc_path = tmp_path / "artifact.tar.gz.cdx.json.asc"
    assert str(asc_path) in capsys.readouterr().out
    signature, _ = openpgp.DetachedSignature.from_armor(asc_path.read_text(encoding="utf-8"))
    signature.verify(key.to_public_key(), b"sbom bytes")


def test_app_sign_uploads_detached_signature(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    key = _ed25519_key()
    key_path = tmp_path / "signing-key.asc"
    key_path.write_text(key.to_armored(), encoding="utf-8")
    config.write(
        {
            "atr": {"host": "example.invalid"},
            "tokens": {"jwt": "dummy_jwt_token"},
        }
    )
    project_url = "https://example.invalid/api/project/get/test-project"
    committee_url = "https://example.invalid/api/committee/keys/test-committee"
    release_url = "https://example.invalid/api/release/get/test-project/2.3.0"
    download_url = "https://example.invalid/download/path/test-project/2.3.0/artifact.tar.gz.cdx.json"
    upload_url = "https://example.invalid/api/release/upload"
    uploaded: list[dict[str, Any]] = []

    def capture_upload(_url: Any, **kwargs: Any) -> aioresponses.CallbackResult:
        uploaded.append(kwargs["json"])
        return aioresponses.CallbackResult(
            status=201,
            payload={
                "endpoint": "/release/upload",
                "revision": {
                    "key": "test-project-2.3.0 00003",
                    "release_key": "test-project-2.3.0",
                    "seq": 3,
                    "number": "00003",
                    "asfuid": "test_asf_uid",
                    "phase": "release_candidate_draft",
                },
            },
        )

    with aioresponses.aioresponses() as mock:
        mock.get(
            project_url,
            status=200,
            payload={"endpoint": "/project/get", "project": {"key": "test-project", "committee_key": "test-committee"}},
        )
        mock.get(
            committee_url,
            status=200,
            payload={"endpoint": "/committee/keys", "keys": [{"fingerprint": key.fingerprint}]},
        )
        mock.get(
            release_url,
            status=200,
            payload={
                "endpoint": "/release/get",
                "release": {
                    "key": "test-project-2.3.0",
                    "project_key": "test-project",
                    "version": "2.3.0",
                    "phase": "release_candidate_draft",
                    "latest_revision_number": "00002",
                },
            },
        )
        mock.get(download_url, status=200, body=b"sbom bytes", content_type="application/octet-stream")
        mock.post(upload_url, callback=capture_upload)
        client.app_sign(
            "test-project", "2.3.0", "artifact.tar.gz.cdx.json", str(tmp_path), key=str(key_path), upload=True
        )

    record = json.loads(capsys.readouterr().out)
    assert record["number"] == "00003"
    assert uploaded[0]["relpath"] == "artifact.tar.gz.cdx.json.asc"
    assert uploaded[0]["expected_revision"] == "00002"
    armored = base64.b64decode(uploaded[0]["content"]).decode("utf-8")
    signature, _ = openpgp.DetachedSignature.from_armor(armored)
    signature.verify(key.to_public_key(), b"sbom bytes")
    assert (tmp_path / "artifact.tar.gz.cdx.json.asc").read_text(encoding="utf-8") == armored


def test_sign_ignores_revoked_uid_certifications() -> None:
    key, _ = openpgp.SecretKey.from_armor(REVOKED_UID_SECRET_KEY_ASC)
    effective = sign._effective_self_signature(key, int(time.time()))
    assert effective is not None
    assert effective.signature_type == "cert-positive"
    assert isinstance(sign.select_signing_component(key), openpgp.SecretKey)


def test_sign_loads_certified_key(tmp_path: pathlib.Path) -> None:
    key_path = tmp_path / "certified.asc"
    key_path.write_text(CERTIFIED_SECRET_KEY_ASC, encoding="utf-8")
    key = sign.load_secret_key(key_path)
    component = sign.select_signing_component(key)
    assert isinstance(component, openpgp.SecretKey)

    armored = sign.sign_detached(b"data", component, None)

    signature, _ = openpgp.DetachedSignature.from_armor(armored)
    signature.verify(key.to_public_key(), b"data")


def test_sign_protected_primary_needs_password() -> None:
    key = _ed25519_key(passphrase="correct horse")
    component = sign.select_signing_component(key)
    assert isinstance(component, openpgp.SecretKey)
    assert sign.component_is_protected(key, component)

    armored = sign.sign_detached(b"data", component, "correct horse")

    signature, _ = openpgp.DetachedSignature.from_armor(armored)
    signature.verify(key.to_public_key(), b"data")


def test_sign_rejects_dummy_primary_export() -> None:
    key, _ = openpgp.SecretKey.from_armor(DUMMY_PRIMARY_SECRET_KEY_ASC)
    assert sign.select_signing_component(key) is None


def test_sign_rejects_expired_primary() -> None:
    key, _ = openpgp.SecretKey.from_armor(EXPIRED_PRIMARY_SECRET_KEY_ASC)
    assert sign.select_signing_component(key) is None


def test_sign_rejects_expired_subkey() -> None:
    key, _ = openpgp.SecretKey.from_armor(EXPIRED_SUBKEY_SECRET_KEY_ASC)
    assert sign.select_signing_component(key) is None


def test_sign_rejects_multi_key_file(tmp_path: pathlib.Path) -> None:
    key_path = tmp_path / "many.pgp"
    key_path.write_bytes(_ed25519_key().to_bytes() + _ed25519_key().to_bytes())

    with pytest.raises(ValueError, match="exactly one key"):
        sign.load_secret_key(key_path)


def test_sign_rejects_v6_certify_only_primary() -> None:
    key = (
        openpgp.SecretKeyParamsBuilder()
        .version(6)
        .key_type(openpgp.KeyType.ed25519())
        .can_sign(False)
        .can_certify(True)
        .primary_user_id("V6 Cert Only <v6@example.invalid>")
        .build()
        .generate()
    )
    assert sign.select_signing_component(key) is None


def test_sign_selects_primary_for_simple_key() -> None:
    key = _ed25519_key()
    component = sign.select_signing_component(key)
    assert isinstance(component, openpgp.SecretKey)
    assert not sign.component_is_protected(key, component)

    armored = sign.sign_detached(b"data", component, None)

    signature, _ = openpgp.DetachedSignature.from_armor(armored)
    assert signature.signature_info().issuer_fingerprints == [key.fingerprint]
    signature.verify(key.to_public_key(), b"data")


def test_sign_selects_signing_subkey() -> None:
    key = _ed25519_key(primary_can_sign=False, with_signing_subkey=True)
    component = sign.select_signing_component(key)
    assert isinstance(component, openpgp.SecretSubkey)
    assert component.fingerprint == key.secret_subkeys[0].fingerprint

    armored = sign.sign_detached(b"data", component, None)

    signature, _ = openpgp.DetachedSignature.from_armor(armored)
    assert signature.signature_info().issuer_fingerprints == [component.fingerprint]
    signature.verify(key.to_public_key(), b"data")


def test_sign_selects_v6_signing_subkey() -> None:
    subkey = openpgp.SubkeyParamsBuilder().version(6).key_type(openpgp.KeyType.ed25519()).can_sign(True).build()
    key = (
        openpgp.SecretKeyParamsBuilder()
        .version(6)
        .key_type(openpgp.KeyType.ed25519())
        .can_sign(False)
        .can_certify(True)
        .primary_user_id("V6 Signer <v6s@example.invalid>")
        .subkey(subkey)
        .build()
        .generate()
    )
    component = sign.select_signing_component(key)
    assert isinstance(component, openpgp.SecretSubkey)

    armored = sign.sign_detached(b"data", component, None)

    signature, _ = openpgp.DetachedSignature.from_armor(armored)
    signature.verify(key.to_public_key(), b"data")


def test_sign_survives_revoked_primary_uid() -> None:
    key, _ = openpgp.SecretKey.from_armor(REVOKED_PRIMARY_UID_SECRET_KEY_ASC)
    effective = sign._effective_self_signature(key, int(time.time()))
    assert effective is not None
    assert effective.signature_type == "cert-positive"
    assert isinstance(sign.select_signing_component(key), openpgp.SecretKey)


def _ed25519_key(
    primary_can_sign: bool = True,
    with_signing_subkey: bool = False,
    passphrase: str | None = None,
) -> openpgp.SecretKey:
    builder = (
        openpgp.SecretKeyParamsBuilder()
        .key_type(openpgp.KeyType.ed25519())
        .can_sign(primary_can_sign)
        .can_certify(True)
        .primary_user_id("Signer <signer@example.invalid>")
        .passphrase(passphrase)
    )
    if with_signing_subkey:
        subkey = openpgp.SubkeyParamsBuilder().key_type(openpgp.KeyType.ed25519()).can_sign(True).build()
        builder = builder.subkey(subkey)
    return builder.build().generate()


def test_task_wait_returns_terminal_task_from_final_poll(monkeypatch: pytest.MonkeyPatch) -> None:
    queued = models.sql.Task(
        id=42,
        task_type=models.sql.TaskType.SBOM_GENERATE,
        task_args={},
        asf_uid="test",
        status=models.sql.TaskStatus.QUEUED,
    )
    completed = models.sql.Task(
        id=42,
        task_type=models.sql.TaskType.SBOM_GENERATE,
        task_args={},
        asf_uid="test",
        status=models.sql.TaskStatus.COMPLETED,
    )

    monkeypatch.setattr(client.api, "task_get", lambda _task_id: types.SimpleNamespace(task=completed))
    monkeypatch.setattr(client.time, "sleep", lambda _seconds: None)

    result = client.task_wait(queued, 0.5)

    assert result.status == models.sql.TaskStatus.COMPLETED


def test_app_vote_start_serializes_template_defaults_and_file_body(
    capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    client.app_set("atr.host", "example.invalid")
    client.app_set("tokens.jwt", "dummy_jwt_token")
    capsys.readouterr()

    vote_url = "https://example.invalid/api/vote/start"
    captured_requests: list[dict[str, Any]] = []
    response_payload = {
        "endpoint": "/vote/start",
        "task": {
            "task_type": "vote_initiate",
            "task_args": {},
            "asf_uid": "test-user",
        },
    }

    def capture_request(_url: Any, **kwargs: Any) -> aioresponses.CallbackResult:
        captured_requests.append(kwargs["json"])
        return aioresponses.CallbackResult(status=201, payload=response_payload)

    body_path = tmp_path / "vote-body.txt"
    body_path.write_text("Custom vote body\n", encoding="utf-8")

    with aioresponses.aioresponses() as mock:
        mock.post(vote_url, callback=capture_request)
        mock.post(vote_url, callback=capture_request)
        client.app_vote_start("test-project", "2.3.1", mailing_list="dev@example.apache.org")
        client.app_vote_start(
            "test-project",
            "2.3.1",
            mailing_list="dev@example.apache.org",
            subject="[VOTE] Custom subject",
            body_file=str(body_path),
        )

    assert captured_requests[0]["subject"] is None
    assert captured_requests[0]["body"] is None
    assert captured_requests[0]["vote_duration"] is None
    assert captured_requests[1]["subject"] == "[VOTE] Custom subject"
    assert captured_requests[1]["body"] == "Custom vote body\n"


def test_app_vote_start_rejects_body_and_body_file(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        client.app_vote_start(
            "test-project",
            "2.3.1",
            mailing_list="dev@example.apache.org",
            body="Literal body",
            body_file="body.txt",
        )

    assert capsys.readouterr().err == "atr: error: Cannot use both --body and --body-file.\n"


def test_app_vote_start_rejects_file_path_as_literal_body(
    capsys: pytest.CaptureFixture[str], tmp_path: pathlib.Path
) -> None:
    body_path = tmp_path / "vote-body.txt"
    body_path.write_text("Custom vote body\n", encoding="utf-8")

    with pytest.raises(SystemExit):
        client.app_vote_start("test-project", "2.3.1", mailing_list="dev@example.apache.org", body=str(body_path))

    assert capsys.readouterr().err == (
        "atr: error: The --body value names an existing file; use --body-file instead.\n"
    )


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


def test_config_signing_key_roundtrip(capsys: pytest.CaptureFixture[str], fixture_config_env: pathlib.Path) -> None:
    client.app_set("signing.key", "/home/user/signing-key.asc")
    capsys.readouterr()

    with config.lock() as cfg:
        assert config.get(cfg, ["signing", "key"]) == "/home/user/signing-key.asc"


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
