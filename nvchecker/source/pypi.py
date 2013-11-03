import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient

PYPI_URL = 'https://pypi.python.org/pypi/%s/json'

def get_version(name, conf, callback):
  repo = conf.get('pypi') or name
  url = PYPI_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_pypi_done, name, callback))

def _pypi_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['info']['version']
  callback(name, version)
