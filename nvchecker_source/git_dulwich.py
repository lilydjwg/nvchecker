# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <6698585+lorepirri@users.noreply.github.com>

import asyncio
from collections.abc import Hashable
from typing import Dict, List, Optional, Tuple, cast

import dulwich.client  # type: ignore[import-not-found]
from dulwich.config import StackedConfig  # type: ignore[import-not-found]

from nvchecker.api import (
    AsyncCache,
    Entry,
    GetVersionError,
    KeyManager,
    RichResult,
    VersionResult,
)


RemoteRefsKey = Tuple[
    str,
    Optional[str],
    Optional[str],
    Optional[str],
]


async def _list_remote_refs_async(
    key: Hashable,
) -> Dict[bytes, bytes]:
    typed_key = cast(RemoteRefsKey, key)
    return await asyncio.to_thread(_list_remote_refs, typed_key)


def _list_remote_refs(
    key: RemoteRefsKey,
) -> Dict[bytes, bytes]:
    git, ref, username, password = key

    config = StackedConfig.default()
    client, path = dulwich.client.get_transport_and_path(
        git,
        config=config,
        username=username,
        password=password,
    )
    result = client.get_refs(path)
    refs = cast(Dict[bytes, bytes], result.refs)

    if ref is None:
        return refs

    return {k: v for k, v in refs.items() if k.decode() == ref}


async def get_version(
    name: str,
    conf: Entry,
    *,
    cache: AsyncCache,
    keymanager: KeyManager,
) -> VersionResult:
    git = conf["git"]

    username = conf.get("username")
    password_key = conf.get("password_key")
    password = keymanager.get_key(password_key) if password_key is not None else None

    use_commit = conf.get("use_commit", False)
    if use_commit:
        ref = conf.get("branch")
        if ref is None:
            ref = "HEAD"
            gitref = None
        else:
            ref = "refs/heads/" + ref
            gitref = ref

        refs = await cache.get(
            (git, ref, username, password),
            _list_remote_refs_async,
        )
        if not refs:
            raise GetVersionError(
                "No ref found in upstream repository.",
                ref=ref,
            )

        version = next(iter(refs.values())).decode()
        return RichResult(
            version=version,
            revision=version,
            gitref=gitref,
        )

    refs = await cache.get(
        (git, None, username, password),
        _list_remote_refs_async,
    )

    versions: List[RichResult] = []
    for refname_bytes, revision in refs.items():
        refname = refname_bytes.decode()
        if not refname.startswith("refs/tags/"):
            continue
        if refname.endswith("^{}"):
            continue

        version = refname.removeprefix("refs/tags/")
        revision_str = revision.decode()
        versions.append(
            RichResult(
                version=version,
                revision=revision_str,
                gitref=refname,
            )
        )

    if not versions:
        raise GetVersionError("No tag found in upstream repository.")

    return versions
