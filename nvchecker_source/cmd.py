# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio

import structlog

from nvchecker.api import GetVersionError

logger = structlog.get_logger(logger_name=__name__)

async def run_cmd(cmd: str) -> str:
  logger.debug('running cmd', cmd=cmd)
  p = await asyncio.create_subprocess_shell(
    cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
  )

  output, error = await p.communicate()
  output_s = output.strip().decode('latin1')
  error_s = error.strip().decode(errors='replace')
  if p.returncode != 0:
    raise GetVersionError(
      'command exited with error',
      cmd=cmd, error=error_s,
      returncode=p.returncode)
  elif not output_s:
    raise GetVersionError(
      'command exited without output',
      cmd=cmd, error=error_s,
      returncode=p.returncode)
  else:
    return output_s

async def get_version(
  name, conf, *, cache, keymanager=None
):
  cmd = conf['cmd']
  return await cache.get(cmd, run_cmd)
