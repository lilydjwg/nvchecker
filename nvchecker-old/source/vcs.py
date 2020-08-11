# MIT licensed
# Copyright (c) 2013-2018 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio
import os.path as _path

from pkg_resources import parse_version
import structlog

from . import conf_cacheable_with_name

logger = structlog.get_logger(logger_name=__name__)
_self_path = _path.dirname(_path.abspath(__file__))
_cmd_prefix = ['/bin/bash', _path.join(_self_path, 'vcs.sh')]

PROT_VER = 1

get_cacheable_conf = conf_cacheable_with_name('vcs')

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

async def get_version(name, conf, **kwargs):
  vcs = conf['vcs'] or ''
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  oldver = conf.get('oldver')
  cmd = _cmd_prefix + [name, vcs]
  if use_max_tag:
    cmd += ["get_tags"]
  p = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
  )

  output, error = await asyncio.wait_for(p.communicate(), 20)
  output = output.strip().decode('latin1')
  error = error.strip().decode('latin1')

  if p.returncode != 0:
    logger.error('command exited with error', output=output,
                 name=name, returncode=p.returncode, error=error)
    return
  else:
    if use_max_tag:
      return [tag for tag in output.split("\n") if tag not in ignored_tags]
    else:
      oldvers = _parse_oldver(oldver)
      if output == oldvers[2]:
        return oldver
      else:
        return "%d.%d.%s" % (oldvers[0], oldvers[1] + 1, output)
