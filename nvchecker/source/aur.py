from functools import partial
import json
import logging

from tornado.httpclient import AsyncHTTPClient
from tornado.escape import url_escape

AUR_URL = 'https://aur.archlinux.org/rpc.php?type=info&arg='
AUR4_URL = 'https://aur4.archlinux.org/rpc.php?type=info&arg='

logger = logging.getLogger(__name__)

def get_version(name, conf, callback):
  aurname = conf.get('aur') or name
  url4 = AUR4_URL + url_escape(aurname)
  AsyncHTTPClient().fetch(url4, partial(_aur4_done, name, aurname, callback))

def _aur4_done(name, aurname, callback, res):
  if res.error:
    raise res.error

  data = json.loads(res.body.decode('utf-8'))

  if not data['results']:
    url = AUR_URL + url_escape(aurname)
    AsyncHTTPClient().fetch(url, partial(_aur_done, name, aurname, callback))
    return

  version = data['results']['Version']
  callback(name, version)

def _aur_done(name, aurname, callback, res):
  if res.error:
    raise res.error

  data = json.loads(res.body.decode('utf-8'))

  if not data['results']:
    logger.error('AUR upstream not found for %s', name)
    callback(name, None)
    return

  version = data['results']['Version']
  callback(name, version)
