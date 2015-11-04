import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient

HACKAGE_URL = 'https://hackage.haskell.org/package/%s/preferred.json'

def get_version(name, conf, callback):
  repo = conf.get('hackage') or name
  url = HACKAGE_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_hackage_done, name, callback))

def _hackage_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['normal-version'][0]
  callback(name, version)
