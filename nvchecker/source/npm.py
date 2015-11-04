import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient

NPM_URL = 'https://registry.npmjs.org/%s'

def get_version(name, conf, callback):
  repo = conf.get('npm') or name
  url = NPM_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_npm_done, name, callback))

def _npm_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['dist-tags']['latest']
  callback(name, version)
