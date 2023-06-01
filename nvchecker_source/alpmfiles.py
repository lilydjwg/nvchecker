# MIT licensed
# Copyright (c) 2023 Pekka Ristola <pekkarr [at] protonmail [dot] com>, et al.

from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
import re
from typing import Tuple, List

from nvchecker.api import GetVersionError

async def get_files(info: Tuple[str, str]) -> List[str]:
  dbpath, pkg = info
  # there's no pyalpm bindings for the file databases
  cmd = ['pacman', '-Flq', '--dbpath', dbpath, pkg]

  p = await create_subprocess_exec(*cmd, stdout = PIPE, stderr = PIPE)
  stdout, stderr = await p.communicate()

  if p.returncode == 0:
    return stdout.decode().splitlines()
  else:
    raise GetVersionError(
      'pacman failed to get file list',
      pkg = pkg,
      cmd = cmd,
      stdout = stdout.decode(errors='replace'),
      stderr = stderr.decode(errors='replace'),
      returncode = p.returncode,
    )

async def get_version(name, conf, *, cache, **kwargs):
  pkg = conf['pkgname']
  repo = conf.get('repo')
  if repo is not None:
    pkg = f'{repo}/{pkg}'
  dbpath = conf.get('dbpath', '/var/lib/pacman')
  regex = re.compile(conf['filename'])
  if regex.groups > 1:
    raise GetVersionError('multi-group regex')
  strip_dir = conf.get('strip_dir', False)

  files = await cache.get((dbpath, pkg), get_files)

  for f in files:
    fn = f.rsplit('/', 1)[-1] if strip_dir else f
    match = regex.fullmatch(fn)
    if match:
      groups = match.groups()
      return groups[0] if len(groups) > 0 else fn

  raise GetVersionError('no file matches specified regex')
