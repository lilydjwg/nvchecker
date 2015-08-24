from functools import partial
import json
import logging

from tornado.httpclient import AsyncHTTPClient
from tornado.escape import url_escape

AUR_URL = 'https://aur.archlinux.org/rpc.php?type=info&arg='

logger = logging.getLogger(__name__)

def get_version(name, conf, callback):
  aurname = conf.get('aur') or name
  strip_release = conf.getboolean('strip-release', False)
  url = AUR_URL + url_escape(aurname)
  AsyncHTTPClient().fetch(
    url, partial(_aur_done, name, strip_release, callback))

def _aur_done(name, strip_release, callback, res):
  if res.error:
    raise res.error

  data = json.loads(res.body.decode('utf-8'))

  if not data['results']:
    logger.error('AUR upstream not found for %s', name)
    callback(name, None)
    return

  version = data['results']['Version']
  if strip_release and '-' in version:
    version = version.rsplit('-', 1)[0]
  callback(name, version)
