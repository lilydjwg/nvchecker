# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import logging
from . import session

logger = logging.getLogger(__name__)

GCODE_URL = 'https://code.google.com/p/%s/source/list'
GCODE_SVN_RE = re.compile(r'<a href="detail\?r=\d+">r(\d+)</a>')

async def get_version(name, conf):
  repo = conf.get('gcode_svn') or name
  url = GCODE_URL % repo
  async with session.get(url) as res:
    data = await res.text()
  m = GCODE_SVN_RE.search(data)
  if m:
    version = m.group(1)
  else:
    logger.error('%s: version not found.', name)
    version = None
  return name, version
