# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio

import structlog

from nvchecker.util import GetVersionError

logger = structlog.get_logger(logger_name=__name__)

def cacher(name, conf):
  return conf['cmd']

async def get_version(name, conf, *, keymanager=None):
  cmd = conf['cmd']
  logger.debug('running cmd', name=name, cmd=cmd)
  p = await asyncio.create_subprocess_shell(
    cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
  )

  output, error = await p.communicate()
  output = output.strip().decode('latin1')
  error = error.strip().decode(errors='replace')
  if p.returncode != 0:
    raise GetVersionError(
      'command exited with error',
      cmd=cmd, error=error,
      name=name, returncode=p.returncode)
  elif not output:
    raise GetVersionError(
      'command exited without output',
      cmd=cmd, error=error,
      name=name, returncode=p.returncode)
  else:
    return output
