# MIT licensed
# Copyright (c) 2013-2020,2025 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio
from functools import partial

import structlog

from nvchecker.api import GetVersionError

async def run_cmd(name: str, cmd: str, timeout: int = 60) -> str:
  logger = structlog.get_logger(
    logger_name = __name__,
    name = name,
    cmd = cmd,
    timeout = timeout,
  )

  logger.debug('running cmd')
  p = await asyncio.create_subprocess_shell(
    cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
  )

  if hasattr(asyncio, 'timeout'):
    # Python 3.11+
    try:
      async with asyncio.timeout(timeout):
        output, error = await p.communicate()
        output_s = output.strip().decode('latin1')
        error_s = error.strip().decode(errors='replace')
    except TimeoutError:
      p.terminate()
      await p.wait()
      raise GetVersionError('command timed out', cmd=cmd)
  else:
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
  return await cache.get(cmd, partial(run_cmd, name))
