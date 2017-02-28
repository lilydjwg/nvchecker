# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import logging
from functools import partial

from tornado.httpclient import AsyncHTTPClient

logger = logging.getLogger(__name__)

GCODE_URL = 'https://code.google.com/p/%s/source/list'
GCODE_SVN_RE = re.compile(r'<a href="detail\?r=\d+">r(\d+)</a>')

def get_version(name, conf, callback):
  repo = conf.get('gcode_svn') or name
  url = GCODE_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_gcodehg_done, name, callback))

def _gcodehg_done(name, callback, res):
  data = res.body.decode('utf-8')
  m = GCODE_SVN_RE.search(data)
  if m:
    version = m.group(1)
  else:
    logger.error('%s: version not found.', name)
    version = None
  callback(name, version)
