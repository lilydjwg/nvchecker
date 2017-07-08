# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import logging
import asyncio

logger = logging.getLogger(__name__)

async def get_version(name, conf):
  cmd = conf['cmd']
  p = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)

  output = (await p.communicate())[0].strip().decode('latin1')
  if p.returncode != 0:
    logger.error('%s: command exited with %d.', name, p.returncode)
    return

  return output
