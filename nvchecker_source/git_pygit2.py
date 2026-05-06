# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <lorepirri@gmail.com>

import asyncio
import tempfile

import pygit2

from nvchecker.api import RichResult, GetVersionError


async def _list_remote_refs_async(key):
    return await asyncio.to_thread(_list_remote_refs, key)


def _list_remote_refs(key):
    git, ref = key

    with tempfile.TemporaryDirectory() as tmpdir:
        repo = pygit2.init_repository(tmpdir, bare=True)
        remote = repo.remotes.create_anonymous(git)
        refs = remote.list_heads()

    if ref is None:
        return refs

    return [r for r in refs if r.name == ref]


async def get_version(name, conf, *, cache, keymanager=None):
    git = conf["git"]

    use_commit = conf.get("use_commit", False)
    if use_commit:
        ref = conf.get("branch")
        if ref is None:
            ref = "HEAD"
            gitref = None
        else:
            ref = "refs/heads/" + ref
            gitref = ref

        refs = await cache.get((git, ref), _list_remote_refs_async)
        if not refs:
            raise GetVersionError("No ref found in upstream repository.", ref=ref)

        version = str(refs[0].oid)
        return RichResult(
            version=version,
            revision=version,
            gitref=gitref,
        )

    refs = await cache.get((git, None), _list_remote_refs_async)

    versions = []
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
