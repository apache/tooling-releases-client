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

import time
from typing import TYPE_CHECKING, Final

import openpgp

if TYPE_CHECKING:
    import pathlib

CERTIFICATION_SIGNATURE_TYPES: Final[frozenset[str]] = frozenset(
    {"cert-generic", "cert-persona", "cert-casual", "cert-positive"}
)
CERTIFICATION_REVOCATION_SIGNATURE_TYPE: Final[str] = "cert-revocation"
SUBKEY_BINDING_SIGNATURE_TYPE: Final[str] = "subkey-binding"
SUBKEY_REVOCATION_SIGNATURE_TYPE: Final[str] = "subkey-revocation"
UNPROTECTED_S2K_USAGE: Final[str] = "unprotected"


def component_is_protected(key: openpgp.SecretKey, component: openpgp.SecretKey | openpgp.SecretSubkey) -> bool:
    if isinstance(component, openpgp.SecretKey):
        return key.primary_secret_s2k().usage != UNPROTECTED_S2K_USAGE
    s2ks = key.secret_subkey_s2ks()
    for index, subkey in enumerate(key.secret_subkeys):
        if subkey.fingerprint == component.fingerprint:
            return s2ks[index].usage != UNPROTECTED_S2K_USAGE
    return False


def load_secret_key(path: pathlib.Path) -> openpgp.SecretKey:
    data = path.read_bytes()
    if data.lstrip().startswith(b"-----BEGIN"):
        keys, _ = openpgp.SecretKey.from_armor_many(data.decode("utf-8"))
    else:
        keys = openpgp.SecretKey.from_bytes_many(data)
    if len(keys) != 1:
        raise ValueError(f"expected exactly one key, found {len(keys)}")
    return keys[0]


def probe_password(component: openpgp.SecretKey | openpgp.SecretSubkey, password: str | None) -> bool:
    try:
        openpgp.DetachedSignature.sign_binary(b"", component, password=password)
    except ValueError:
        return False
    return True


def select_signing_component(key: openpgp.SecretKey) -> openpgp.SecretKey | openpgp.SecretSubkey | None:
    now = int(time.time())
    if key.revocation_signature_infos():
        return None
    effective = _effective_self_signature(key, now)
    if _expired(key.created_at, effective, now):
        return None
    s2ks = key.secret_subkey_s2ks()
    subkeys = [
        subkey
        for index, subkey in enumerate(key.secret_subkeys)
        if _subkey_usable(subkey, now) and _secret_available(s2ks[index])
    ]
    if subkeys:
        return max(subkeys, key=lambda subkey: subkey.created_at)
    if _flags_allow_signing(effective) and _secret_available(key.primary_secret_s2k()):
        return key
    return None


def sign_detached(data: bytes, component: openpgp.SecretKey | openpgp.SecretSubkey, password: str | None) -> str:
    signature = openpgp.DetachedSignature.sign_binary(data, component, password=password, hash_algorithm="sha512")
    return signature.to_armored()


def _effective_self_signature(key: openpgp.SecretKey, now: int) -> openpgp.SignatureInfo | None:
    fingerprint = key.fingerprint.lower()
    key_id = key.key_id.lower()
    direct = [
        signature for signature in key.direct_signature_infos() if _signature_is_self(signature, fingerprint, key_id)
    ]
    if key.version >= 6:
        return _latest_signature(direct, now)
    active_bindings = [
        binding for binding in key.user_bindings() if not _binding_revoked(binding, fingerprint, key_id, now)
    ]
    primary_bindings = [binding for binding in active_bindings if binding.is_primary]
    chosen_bindings = primary_bindings or active_bindings
    bindings = [
        signature
        for binding in chosen_bindings
        for signature in binding.signatures
        if _signature_is_self(signature, fingerprint, key_id)
        and (signature.signature_type in CERTIFICATION_SIGNATURE_TYPES)
    ]
    if bindings:
        return _latest_signature(bindings, now)
    return _latest_signature(direct, now)


def _binding_revoked(binding: openpgp.UserBindingInfo, fingerprint: str, key_id: str, now: int) -> bool:
    candidates = [
        signature
        for signature in binding.signatures
        if _signature_is_self(signature, fingerprint, key_id)
        and (
            (signature.signature_type in CERTIFICATION_SIGNATURE_TYPES)
            or (signature.signature_type == CERTIFICATION_REVOCATION_SIGNATURE_TYPE)
        )
    ]
    latest = _latest_signature(candidates, now)
    return (latest is not None) and (latest.signature_type == CERTIFICATION_REVOCATION_SIGNATURE_TYPE)


def _expired(created_at: int, signature: openpgp.SignatureInfo | None, now: int) -> bool:
    if signature is None:
        return False
    expiration = signature.key_expiration_seconds
    if not expiration:
        return False
    return (created_at + expiration) <= now


def _flags_allow_signing(signature: openpgp.SignatureInfo | None) -> bool:
    if signature is None:
        return False
    flags = signature.key_flags
    declares_any = (
        flags.certify
        or flags.sign
        or flags.encrypt_communications
        or flags.encrypt_storage
        or flags.authenticate
        or flags.timestamping
    )
    if not declares_any:
        return True
    return flags.sign


def _latest_signature(signatures: list[openpgp.SignatureInfo], now: int) -> openpgp.SignatureInfo | None:
    valid = [signature for signature in signatures if not _signature_expired(signature, now)]
    if not valid:
        return None
    return max(valid, key=lambda signature: signature.creation_time or 0)


def _secret_available(s2k: openpgp.S2kParams) -> bool:
    string_to_key = s2k.string_to_key
    if string_to_key is None:
        return True
    return string_to_key.kind != "private"


def _signature_expired(signature: openpgp.SignatureInfo, now: int) -> bool:
    expiration = signature.signature_expiration_seconds
    if not expiration:
        return False
    creation = signature.creation_time or 0
    return (creation + expiration) <= now


def _signature_is_self(signature: openpgp.SignatureInfo, fingerprint: str, key_id: str) -> bool:
    fingerprints = {issuer.lower() for issuer in signature.issuer_fingerprints}
    key_ids = {issuer.lower() for issuer in signature.issuer_key_ids}
    return (fingerprint in fingerprints) or (key_id in key_ids)


def _subkey_usable(subkey: openpgp.SecretSubkey, now: int) -> bool:
    if any(signature.signature_type == SUBKEY_REVOCATION_SIGNATURE_TYPE for signature in subkey.signatures):
        return False
    bindings = [
        signature for signature in subkey.signatures if signature.signature_type == SUBKEY_BINDING_SIGNATURE_TYPE
    ]
    binding = _latest_signature(bindings, now)
    if not _flags_allow_signing(binding):
        return False
    return not _expired(subkey.created_at, binding, now)
