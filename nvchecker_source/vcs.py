# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio
import os.path as _path

from nvchecker.api import GetVersionError

_self_path = _path.dirname(_path.abspath(__file__))
_cmd_prefix = ['/bin/bash', _path.join(_self_path, 'vcs.sh')]

PROT_VER = 1

def _parse_oldver(oldver):
  if oldver is None:
    return PROT_VER, 0, ''
  try:
    prot_ver, count, ver = oldver.split('.', maxsplit=2)
    prot_ver = int(prot_ver)
    count = int(count)
  except Exception:
    return PROT_VER, 0, ''
  if prot_ver != PROT_VER:
    return PROT_VER, 0, ver
  return PROT_VER, count, ver

async def get_version(name, conf, *, cache, **kwargs):
  vcs = conf.get('vcs', '')
  use_max_tag = conf.get('use_max_tag', False)
  oldver = conf.get('oldver')
  cmd = _cmd_prefix + [name, vcs]
  if use_max_tag:
    cmd += ["get_tags"]

  output = await cache.get(tuple(cmd), run_cmd)

  if use_max_tag:
    return [tag for tag in output.split("\n")]
  else:
    oldvers = _parse_oldver(oldver)
    if output == oldvers[2]:
      return oldver
    else:
      return "%d.%d.%s" % (oldvers[0], oldvers[1] + 1, output)

async def run_cmd(cmd):
  p = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
  )

  output, error = await asyncio.wait_for(p.communicate(), 20)
  output = output.strip().decode('latin1')
  error = error.strip().decode('latin1')

  if p.returncode != 0:
    raise GetVersionError(
      'command exited with error', output=output,
      returncode=p.returncode, error=error)
  else:
    return output
