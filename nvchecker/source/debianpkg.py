# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

from functools import partial
import logging
import json

from tornado.httpclient import AsyncHTTPClient

logger = logging.getLogger(__name__)

URL = 'https://sources.debian.net/api/src/%(pkgname)s/?suite=%(suite)s'

def get_version(name, conf, callback):
  pkg = conf.get('debianpkg') or name
  strip_release = conf.getboolean('strip-release', False)
  suite = conf.get('suite') or "sid"
  url = URL % {"pkgname": pkg, "suite": suite}
  AsyncHTTPClient().fetch(
    url, partial(_pkg_done, name, strip_release, callback))

def _pkg_done(name, strip_release, callback, res):
  if res.error:
    raise res.error

  data = json.loads(res.body.decode('utf-8'))

  if not data.get('versions'):
    logger.error('Debian package not found: %s', name)
    callback(name, None)
    return

  r = data['versions'][0]
  if strip_release:
    version = r['version'].split("-")[0]
  else:
    version = r['version']

  callback(name, version)
