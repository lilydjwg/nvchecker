# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

from .cmd import run_cmd # type: ignore

async def get_version(
  name, conf, *, cache, keymanager=None
):
  git = conf['git']

  use_commit = conf.get('use_commit', False)
  if use_commit:
    ref = conf.get('branch')
    if ref is None:
      ref = 'HEAD'
    else:
      ref = 'refs/heads/' + ref
    cmd = f"git ls-remote {git} {ref}"
    data = await cache.get(cmd, run_cmd)
    return data.split(None, 1)[0]
  else:
    cmd = f"git ls-remote --tags --refs {git}"
    data = await cache.get(cmd, run_cmd)
    versions = [line.split("refs/tags/")[1] for line in data.splitlines()]
    return versions
