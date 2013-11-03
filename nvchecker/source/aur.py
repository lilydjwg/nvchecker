from functools import partial
import json

from tornado.httpclient import AsyncHTTPClient

AUR_URL = 'https://aur.archlinux.org/rpc.php?type=info&arg='

def get_version(name, conf, callback):
  aurname = conf.get('aur') or name
  url = AUR_URL + aurname
  AsyncHTTPClient().fetch(url, partial(_aur_done, name, callback))

def _aur_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['results']['Version']
  callback(name, version)
