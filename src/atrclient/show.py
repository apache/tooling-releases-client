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

import json
import sys
from typing import NoReturn

import atrclient.basic as basic
import atrclient.config as config
import atrclient.models.schema as schema


def error_and_exit(message: str, code: int = 1) -> NoReturn:
    sys.stderr.write(f"atr: error: {message}\n")
    sys.stderr.flush()
    raise SystemExit(code)


def json_or_message(data: basic.JSON | schema.Strict, message: str | None = None) -> None:
    cfg = config.read()
    output_json = config.get(cfg, ["output", "json"])
    if (output_json is True) or (message is None):
        if isinstance(data, schema.Strict):
            print(json.dumps(data.model_dump(), indent=None))
        else:
            print(json.dumps(data, indent=None))
    else:
        print(message)


def warning(message: str) -> None:
    sys.stderr.write(f"atr: warning: {message}\n")
    sys.stderr.flush()
