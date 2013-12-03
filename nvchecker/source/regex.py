import re
import sre_constants
import logging
import urllib.parse
from functools import partial

from pkg_resources import parse_version
from tornado.httpclient import AsyncHTTPClient

from .base import pycurl

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

  httpclient.fetch(conf['url'], partial(
    _got_version, name, r, encoding, callback
  ), **kwargs)

def _got_version(name, regex, encoding, callback, res):
  version = None
  try:
    body = res.body.decode(encoding)
    try:
      version = max(regex.findall(body), key=parse_version)
    except ValueError:
      logger.error('%s: version string not found.', name)
  finally:
    callback(name, version)
