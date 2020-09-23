# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

from .cmd import run_cmd # type: ignore

async def get_version(
  name, conf, *, cache, keymanager=None
):
  git = conf['git']
  cmd = f"git ls-remote -t --refs {git}"
  data = await cache.get(cmd, run_cmd)
  versions = list(map(lambda line: line.split("refs/tags/")[1], data.split("\n")))
  return versions
