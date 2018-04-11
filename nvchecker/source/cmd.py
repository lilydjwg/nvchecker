# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio

import structlog

logger = structlog.get_logger(logger_name=__name__)

async def get_version(name, conf):
  cmd = conf['cmd']
  p = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)

  output = (await p.communicate())[0].strip().decode('latin1')
  if p.returncode != 0:
    logger.error('command exited with error',
                 name=name, returncode=p.returncode)
    return

  return output
