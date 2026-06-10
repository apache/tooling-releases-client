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

import pathlib
import types
from typing import Any

import aiohttp
import aioresponses.core
import pytest


class ClientResponseShim(aiohttp.ClientResponse):
    # As of aiohttp 3.14, stream_writer is now a required argument
    # Since aioresponses does not yet pass it as of 0.7.8, we need this shim
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("stream_writer", types.SimpleNamespace(output_size=0))
        super().__init__(*args, **kwargs)


setattr(aioresponses.core, "ClientResponse", ClientResponseShim)


@pytest.fixture
def fixture_config_env(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> pathlib.Path:
    path = tmp_path / "atr.yaml"
    monkeypatch.setenv("ATR_CLIENT_CONFIG_PATH", str(path))
    return path
