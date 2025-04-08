# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

from functools import partial

from .cmd import run_cmd

from nvchecker.api import RichResult

async def get_version(
  name, conf, *, cache, keymanager=None
):
  git = conf['git']

  use_commit = conf.get('use_commit', False)
  if use_commit:
    ref = conf.get('branch')
    if ref is None:
      ref = 'HEAD'
      gitref = None
    else:
      ref = 'refs/heads/' + ref
      gitref = ref
    cmd = f"git ls-remote {git} {ref}"
    data = await cache.get(cmd, partial(run_cmd, name))
    version = data.split(None, 1)[0]
    return RichResult(
      version = version,
      revision = version,
      gitref = gitref,
    )
  else:
    cmd = f"git ls-remote --tags --refs {git}"
    data = await cache.get(cmd, partial(run_cmd, name))
    versions = []
    for line in data.splitlines():
      revision, version = line.split("\trefs/tags/", 1)
      versions.append(RichResult(
        version = version,
        revision = revision,
        gitref = f"refs/tags/{version}",
      ))
    return versions
