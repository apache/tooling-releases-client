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

from typing import Any, TypeGuard

type JSON = dict[str, Any] | list[Any] | str | int | float | bool | None


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
