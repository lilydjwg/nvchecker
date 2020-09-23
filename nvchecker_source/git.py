# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

import re
from nvchecker_source.cmd import run_cmd

async def get_version(
  name, conf, *, cache, keymanager=None
):
  git = conf['git']
  cmd = f"git ls-remote -t --refs {git}"
  data = await cache.get(cmd, run_cmd)
  regex = "(?<=refs/tags/).*$"

  return re.findall(regex, data)
