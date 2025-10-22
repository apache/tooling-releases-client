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

import aiohttp

import atrclient.basic as basic
import atrclient.models.schema as schema
import atrclient.show as show


async def get(url: str, jwt_token: str | None, verify_ssl: bool = True) -> basic.JSON:
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
                        show.error_and_exit(f"{error_message} from {url}")
                    else:
                        show.error_and_exit(f"Request failed: {resp.status} {url}\n{text}")
                except json.JSONDecodeError:
                    show.error_and_exit(f"Request failed: {resp.status} {url}\n{text}")
            data = await resp.json()
            if not basic.is_json(data):
                show.error_and_exit(f"Unexpected API response: {data}")
            return data


async def get_url(url: str, verify_ssl: bool = True) -> bytes:
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            if response.status != 200:
                show.error_and_exit(f"URL not found: {url}")
            return await response.read()


async def post(url: str, args: schema.Strict, jwt_token: str | None, verify_ssl: bool = True) -> basic.JSON:
    return await post_json(url, args.model_dump(mode="json"), jwt_token, verify_ssl)


async def post_json(url: str, args: basic.JSON, jwt_token: str | None, verify_ssl: bool = True) -> basic.JSON:
    connector = None if verify_ssl else aiohttp.TCPConnector(ssl=False)
    headers = {}
    if jwt_token is not None:
        headers["Authorization"] = f"Bearer {jwt_token}"
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        async with session.post(url, json=args) as resp:
            if resp.status not in (200, 201):
                text = await resp.text()
                show.error_and_exit(f"Error message from the API:\n{resp.status} {url}\n{text}")

            try:
                data = await resp.json()
                if not basic.is_json(data):
                    show.error_and_exit(f"Unexpected API response: {data}")
                return data
            except Exception as e:
                show.error_and_exit(f"Python error getting API response:\n{resp.status} {url}\n{e}")
