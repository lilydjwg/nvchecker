# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import re
import sre_constants
import logging
import urllib.parse
from functools import partial

from tornado.httpclient import AsyncHTTPClient

from .base import pycurl
from ..sortversion import sort_version_keys

logger = logging.getLogger(__name__)

def get_version(name, conf, callback):
  try:
    r = re.compile(conf['regex'])
  except sre_constants.error:
    logger.warn('%s: bad regex, skipped.', name, exc_info=True)
    callback(name, None)
    return

  encoding = conf.get('encoding', 'latin1')
  httpclient = AsyncHTTPClient()

  kwargs = {}
  if conf.get('proxy'):
    if pycurl:
      host, port = urllib.parse.splitport(conf['proxy'])
      kwargs['proxy_host'] = host
      kwargs['proxy_port'] = int(port)
    else:
      logger.warn('%s: proxy set but not used because pycurl is unavailable.', name)
  if conf.get('user_agent'):
    kwargs['user_agent'] = conf['user_agent']
  sort_version_key = sort_version_keys[conf.get("sort_version_key", "parse_version")]

  httpclient.fetch(conf['url'], partial(
    _got_version, name, r, encoding, sort_version_key, callback
  ), **kwargs)

def _got_version(name, regex, encoding, sort_version_key, callback, res):
  version = None
  try:
    body = res.body.decode(encoding)
    try:
      version = max(regex.findall(body), key=sort_version_key)
    except ValueError:
      logger.error('%s: version string not found.', name)
  finally:
    callback(name, version)
