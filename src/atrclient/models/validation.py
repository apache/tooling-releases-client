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

import re
from typing import Final

import hyperscan

MAX_IGNORE_PATTERN_LENGTH: Final[int] = 128


class HyperscanPattern:
    __slots__ = ("_db",)

    def __init__(self, db: hyperscan.Database) -> None:
        self._db = db

    def search(self, value: str):
        matched = False

        def on_match(_id: int, _start: int, _end: int, _flags: int, _context: object) -> bool:
            nonlocal matched
            matched = True
            return True

        try:
            self._db.scan(value.encode("utf-8"), on_match)
        except hyperscan.ScanTerminated:
            return True
        except hyperscan.HyperscanError:
            return None

        return True if matched else None


def compile_ignore_pattern(pattern: str):
    # TODO: This requires importing Hyperscan in atr/models
    # We want to avoid such dependencies
    # But if we move this out, we can't do full validation in the models
    if len(pattern) > MAX_IGNORE_PATTERN_LENGTH:
        raise ValueError(f"Pattern exceeds {MAX_IGNORE_PATTERN_LENGTH} characters")
    if pattern.startswith("^") or pattern.endswith("$"):
        regex_pattern = pattern
    else:
        regex_pattern = re.escape(pattern).replace(r"\*", ".*")
        # Should maybe add .replace(r"\?", ".?")
    # We must turn off Chimera mode to avoid backtracking
    db = hyperscan.Database(mode=hyperscan.HS_MODE_BLOCK, chimera=False)
    try:
        db.compile([regex_pattern])
    except hyperscan.HyperscanError as exc:
        raise ValueError(f"Invalid ignore pattern: {exc}") from exc
    return HyperscanPattern(db)


def validate_ignore_pattern(pattern: str) -> None:
    """Raise an exception if the pattern is invalid."""
    if pattern == "!":
        return
    raw_pattern = pattern
    if raw_pattern.startswith("!"):
        raw_pattern = raw_pattern[1:]
    compile_ignore_pattern(raw_pattern)
