# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <6698585+lorepirri@users.noreply.github.com>

import asyncio
import tempfile
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union, cast

import pygit2

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


@dataclass(frozen=True)
class RemoteRef:
    name: str
    oid: Any


async def _list_remote_refs_async(
    key: Hashable,
) -> List[RemoteRef]:
    typed_key = cast(RemoteRefsKey, key)
    return await asyncio.to_thread(_list_remote_refs, typed_key)


def _normalize_ref(ref: Any) -> RemoteRef:
    if isinstance(ref, dict):
        return RemoteRef(name=ref["name"], oid=ref["oid"])

    return RemoteRef(name=ref.name, oid=ref.oid)


def _list_heads(
    remote: Any,
    callbacks: Optional[pygit2.RemoteCallbacks] = None,
) -> List[RemoteRef]:
    if hasattr(remote, "list_heads"):
        refs = remote.list_heads(callbacks=callbacks)
    else:
        refs = remote.ls_remotes(callbacks=callbacks)

    return [_normalize_ref(ref) for ref in refs]


def _list_remote_refs(
    key: RemoteRefsKey,
) -> List[RemoteRef]:
    git, ref, username, password = key

    callbacks = None
    if username is not None and password is not None:
        callbacks = pygit2.RemoteCallbacks(
            credentials=pygit2.UserPass(username, password),
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        repo = pygit2.init_repository(tmpdir, bare=True)
        remote = repo.remotes.create_anonymous(git)
        refs = _list_heads(remote, callbacks)

    if ref is None:
        return refs

    return [remote_ref for remote_ref in refs if remote_ref.name == ref]


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
    if (username is None) != (password_key is None):
        raise GetVersionError("username and password_key must be specified together")
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
            raise GetVersionError("No ref found in upstream repository.", ref=ref)

        version = str(refs[0].oid)
        return RichResult(
            version=version,
            revision=version,
            gitref=gitref,
        )

    refs = await cache.get(
        (git, None, username, password),
        _list_remote_refs_async,
    )

    versions: List[Union[str, RichResult]] = []
    for ref in refs:
        if not ref.name.startswith("refs/tags/"):
            continue
        if ref.name.endswith("^{}"):
            continue

        version = ref.name.removeprefix("refs/tags/")
        revision = str(ref.oid)
        versions.append(
            RichResult(
                version=version,
                revision=revision,
                gitref=ref.name,
            )
        )

    if not versions:
        raise GetVersionError("No tag found in upstream repository.")

    return versions
