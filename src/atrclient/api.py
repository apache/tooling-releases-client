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
import functools
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

import aiohttp
import pydantic

import atrclient.basic as basic
import atrclient.config as config
import atrclient.models as models
import atrclient.show as show
import atrclient.web as web


class ApiCore:
    def __init__(self, path: str):
        host, verify_ssl = config.host_get()
        self.url = f"https://{host}/api{path}"
        self.verify_ssl = verify_ssl


class ApiGet(ApiCore):
    def get(self, *args: str, **kwargs: str | None) -> basic.JSON:
        url = self.url + "/" + "/".join(args)
        for value in kwargs.values():
            if value is not None:
                url += f"/{value}"
        jwt_value = None
        return asyncio.run(web.get(url, jwt_value, self.verify_ssl))


class ApiPost(ApiCore):
    def post(self, args: models.schema.Strict) -> basic.JSON:
        jwt_value = config.jwt_usable()
        return asyncio.run(web.post(self.url, args, jwt_value, self.verify_ssl))


A = TypeVar("A", bound=models.schema.Strict)
R = TypeVar("R", bound=models.api.Results)


def get(path: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: str, **kwargs: str | None) -> R:
            api_instance = ApiGet(path)
            try:
                response = func(api_instance, *args, **kwargs)
            except pydantic.ValidationError as e:
                error_summary = "\n".join([f"  - {err['loc'][1]}: {err['msg']}" for err in e.errors()])
                show.error_and_exit(f"API response failed validation:\n{error_summary}")
            except (aiohttp.ClientError, models.api.ResultsTypeError) as e:
                show.error_and_exit(f"Unexpected API GET response: {e}")
            else:
                return response

        return wrapper

    return decorator


def post(path: str) -> Callable[[Callable[[ApiPost, A], R]], Callable[[A], R]]:
    def decorator(func: Callable[[ApiPost, A], R]) -> Callable[[A], R]:
        def wrapper(args: A) -> R:
            api_instance = ApiPost(path)
            try:
                response = func(api_instance, args)
            except (pydantic.ValidationError, models.api.ResultsTypeError) as e:
                show.error_and_exit(f"Unexpected API POST response: {e}")
            return response

        return wrapper

    return decorator


@get("/checks/list")
def checks_list(api: ApiGet, project: str, version: str, revision: str) -> models.api.ChecksListResults:
    response = api.get(project, version, revision)
    return models.api.validate_checks_list(response)


@get("/checks/ongoing")
def checks_ongoing(
    api: ApiGet, project: str, version: str, revision: str | None = None
) -> models.api.ChecksOngoingResults:
    response = api.get(project, version, revision=revision)
    return models.api.validate_checks_ongoing(response)


@post("/distribution/record")
def distribution_record(api: ApiPost, args: models.api.DistributionRecordArgs) -> models.api.DistributionRecordResults:
    response = api.post(args)
    return models.api.validate_distribution_record(response)


@post("/ignore/add")
def ignore_add(api: ApiPost, args: models.api.IgnoreAddArgs) -> models.api.IgnoreAddResults:
    response = api.post(args)
    return models.api.validate_ignore_add(response)


@post("/ignore/delete")
def ignore_delete(api: ApiPost, args: models.api.IgnoreDeleteArgs) -> models.api.IgnoreDeleteResults:
    response = api.post(args)
    return models.api.validate_ignore_delete(response)


@get("/ignore/list")
def ignore_list(api: ApiGet, committee: str) -> models.api.IgnoreListResults:
    response = api.get(committee)
    return models.api.validate_ignore_list(response)


@post("/key/add")
def key_add(api: ApiPost, args: models.api.KeyAddArgs) -> models.api.KeyAddResults:
    response = api.post(args)
    return models.api.validate_key_add(response)


@post("/key/delete")
def key_delete(api: ApiPost, args: models.api.KeyDeleteArgs) -> models.api.KeyDeleteResults:
    response = api.post(args)
    return models.api.validate_key_delete(response)


@get("/key/get")
def key_get(api: ApiGet, fingerprint: str) -> models.api.KeyGetResults:
    response = api.get(fingerprint)
    return models.api.validate_key_get(response)


@post("/keys/upload")
def keys_upload(api: ApiPost, args: models.api.KeysUploadArgs) -> models.api.KeysUploadResults:
    response = api.post(args)
    return models.api.validate_keys_upload(response)


@get("/keys/user")
def keys_user(api: ApiGet, asf_uid: str) -> models.api.KeysUserResults:
    response = api.get(asf_uid)
    return models.api.validate_keys_user(response)


@get("/project/releases")
def project_releases(api: ApiGet, project: str) -> models.api.ProjectReleasesResults:
    response = api.get(project)
    return models.api.validate_project_releases(response)


@post("/release/announce")
def release_announce(api: ApiPost, args: models.api.ReleaseAnnounceArgs) -> models.api.ReleaseAnnounceResults:
    response = api.post(args)
    return models.api.validate_release_announce(response)


@post("/release/create")
def release_create(api: ApiPost, args: models.api.ReleaseCreateArgs) -> models.api.ReleaseCreateResults:
    response = api.post(args)
    return models.api.validate_release_create(response)


@post("/release/delete")
def release_delete(api: ApiPost, args: models.api.ReleaseDeleteArgs) -> models.api.ReleaseDeleteResults:
    response = api.post(args)
    return models.api.validate_release_delete(response)


@post("/release/draft/delete")
def release_draft_delete(api: ApiPost, args: models.api.ReleaseDraftDeleteArgs) -> models.api.ReleaseDraftDeleteResults:
    response = api.post(args)
    return models.api.validate_release_draft_delete(response)


@get("/release/paths")
def release_paths(
    api: ApiGet, project: str, version: str, revision: str | None = None
) -> models.api.ReleasePathsResults:
    response = api.get(project, version, revision=revision)
    return models.api.validate_release_paths(response)


@get("/release/get")
def release_get(api: ApiGet, project: str, version: str) -> models.api.ReleaseGetResults:
    response = api.get(project, version)
    return models.api.validate_release_get(response)


@get("/release/revisions")
def release_revisions(api: ApiGet, project: str, version: str) -> models.api.ReleaseRevisionsResults:
    response = api.get(project, version)
    return models.api.validate_release_revisions(response)


@post("/release/upload")
def release_upload(api: ApiPost, args: models.api.ReleaseUploadArgs) -> models.api.ReleaseUploadResults:
    response = api.post(args)
    return models.api.validate_release_upload(response)


@post("/signature/provenance")
def signature_provenance(
    api: ApiPost, args: models.api.SignatureProvenanceArgs
) -> models.api.SignatureProvenanceResults:
    response = api.post(args)
    return models.api.validate_signature_provenance(response)


@post("/ssh-key/add")
def ssh_key_add(api: ApiPost, args: models.api.SshKeyAddArgs) -> models.api.SshKeyAddResults:
    response = api.post(args)
    return models.api.validate_ssh_key_add(response)


@post("/ssh-key/delete")
def ssh_key_delete(api: ApiPost, args: models.api.SshKeyDeleteArgs) -> models.api.SshKeyDeleteResults:
    response = api.post(args)
    return models.api.validate_ssh_key_delete(response)


@get("/ssh-keys/list")
def ssh_keys_list(api: ApiGet, asf_uid: str) -> models.api.SshKeysListResults:
    response = api.get(asf_uid)
    return models.api.validate_ssh_keys_list(response)


@post("/vote/resolve")
def vote_resolve(api: ApiPost, args: models.api.VoteResolveArgs) -> models.api.VoteResolveResults:
    response = api.post(args)
    return models.api.validate_vote_resolve(response)


@post("/vote/start")
def vote_start(api: ApiPost, args: models.api.VoteStartArgs) -> models.api.VoteStartResults:
    response = api.post(args)
    return models.api.validate_vote_start(response)


@post("/vote/tabulate")
def vote_tabulate(api: ApiPost, args: models.api.VoteTabulateArgs) -> models.api.VoteTabulateResults:
    response = api.post(args)
    return models.api.validate_vote_tabulate(response)
