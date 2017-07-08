# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import logging
import asyncio
from pkg_resources import parse_version

import os.path as _path

logger = logging.getLogger(__name__)
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
    except:
        return PROT_VER, 0, ''
    if prot_ver != PROT_VER:
        return PROT_VER, 0, ver
    return PROT_VER, count, ver

async def get_version(name, conf):
  vcs = conf['vcs']
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  oldver = conf.get('oldver')
  cmd = _cmd_prefix + [name, vcs]
  if use_max_tag:
    cmd += ["get_tags"]
  p = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)

  output = (await p.communicate())[0].strip().decode('latin1')
  if p.returncode != 0:
    logger.error('%s: command exited with %d.', name, p.returncode)
    return
  else:
    if use_max_tag:
      data = [tag for tag in output.split("\n") if tag not in ignored_tags]
      data.sort(key=parse_version)
      version = data[-1]
      return version
    else:
      oldver = _parse_oldver(oldver)
      if output == oldver[2]:
        return
      else:
        return "%d.%d.%s" % (oldver[0], oldver[1] + 1, output)
