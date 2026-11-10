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

import sys
import zipfile
from typing import Final

_METADATA: Final = ("METADATA", "RECORD", "WHEEL", "entry_points.txt", "licenses/LICENSE", "licenses/NOTICE")
_PACKAGE: Final = (
    "atrclient/__init__.py",
    "atrclient/__main__.py",
    "atrclient/api.py",
    "atrclient/basic.py",
    "atrclient/client.py",
    "atrclient/config.py",
    "atrclient/models/__init__.py",
    "atrclient/models/api.py",
    "atrclient/models/args.py",
    "atrclient/models/attestable.py",
    "atrclient/models/basic.py",
    "atrclient/models/calver.py",
    "atrclient/models/cap.py",
    "atrclient/models/checkdata.py",
    "atrclient/models/cle.py",
    "atrclient/models/distribution.py",
    "atrclient/models/github.py",
    "atrclient/models/helpers.py",
    "atrclient/models/mail.py",
    "atrclient/models/results.py",
    "atrclient/models/safe.py",
    "atrclient/models/schema.py",
    "atrclient/models/sql.py",
    "atrclient/models/tabulate.py",
    "atrclient/models/unsafe.py",
    "atrclient/models/validation.py",
    "atrclient/results.py",
    "atrclient/show.py",
    "atrclient/sign.py",
    "atrclient/web.py",
)


def main() -> None:
    with zipfile.ZipFile(sys.argv[1]) as wheel:
        names = [name for name in wheel.namelist() if not name.endswith("/")]
    if len(names) != len(set(names)):
        sys.exit("ERROR: the wheel contains duplicate entries")
    dist_infos = {name.split("/")[0] for name in names if name.split("/")[0].endswith(".dist-info")}
    if (len(dist_infos) != 1) or not next(iter(dist_infos)).startswith("apache_trusted_releases-"):
        sys.exit(f"ERROR: expected one apache_trusted_releases .dist-info directory, found {sorted(dist_infos)}")
    dist_info = dist_infos.pop()
    expected = {*_PACKAGE, *(f"{dist_info}/{name}" for name in _METADATA)}
    found = set(names)
    errors = [f"missing {name}" for name in sorted(expected - found)]
    errors.extend(f"unexpected {name}" for name in sorted(found - expected))
    if errors:
        sys.exit("\n".join(f"ERROR: {error}" for error in errors))


if __name__ == "__main__":
    main()
