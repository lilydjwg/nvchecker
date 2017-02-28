# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import time
import logging
from functools import partial

from tornado.httpclient import AsyncHTTPClient

logger = logging.getLogger(__name__)

GCODE_URL = 'https://code.google.com/p/%s/source/list'
GCODE_HG_RE = re.compile(
  r'<a onclick="cancelBubble=true" href="detail\?r=[0-9a-f]+">([^<]+)</a>')

def get_version(name, conf, callback):
  repo = conf.get('gcode_hg') or name
  url = GCODE_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_gcodehg_done, name, callback))

def _gcodehg_done(name, callback, res):
  data = res.body.decode('utf-8')
  m = GCODE_HG_RE.search(data)
  if m:
    t = time.strptime(m.group(1), '%b %d, %Y')
    version = time.strftime('%Y%m%d', t)
  else:
    logger.error('%s: version not found.', name)
    version = None
  callback(name, version)
