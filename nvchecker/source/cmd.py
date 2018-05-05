# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio

import structlog

logger = structlog.get_logger(logger_name=__name__)

async def get_version(name, conf, **kwargs):
  cmd = conf['cmd']
  p = await asyncio.create_subprocess_shell(
    cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
  )

  output, error = await p.communicate()
  output = output.strip().decode('latin1')
  error = error.strip().decode(errors='replace')
  if p.returncode != 0:
    logger.error('command exited with error',
                 cmd=cmd, error=error,
                 name=name, returncode=p.returncode)
  elif not output:
    logger.error('command exited without output',
                 cmd=cmd, error=error,
                 name=name, returncode=p.returncode)
  else:
    return output
