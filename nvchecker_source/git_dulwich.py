# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <lorepirri@gmail.com>

import asyncio

import dulwich.client

from nvchecker.api import RichResult, GetVersionError


async def _list_remote_refs_async(key):
    return await asyncio.to_thread(_list_remote_refs, key)


def _list_remote_refs(key):
    git, ref = key

    client, path = dulwich.client.get_transport_and_path(git)
    result = client.get_refs(path)
    refs = result.refs

    if ref is None:
        return refs

    return {k: v for k, v in refs.items() if k.decode() == ref}


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

        version = next(iter(refs.values())).decode()
        return RichResult(
            version=version,
            revision=version,
            gitref=gitref,
        )

    refs = await cache.get((git, None), _list_remote_refs_async)

    versions = []
    for refname, revision in refs.items():
        refname = refname.decode()
        if not refname.startswith("refs/tags/"):
            continue
        if refname.endswith("^{}"):
            continue

        version = refname.removeprefix("refs/tags/")
        revision = revision.decode()
        versions.append(
            RichResult(
                version=version,
                revision=revision,
                gitref=refname,
            )
        )

    if not versions:
        raise GetVersionError("No tag found in upstream repository.")

    return versions
