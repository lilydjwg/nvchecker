import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient

GEMS_URL = 'https://rubygems.org/api/v1/versions/%s.json'

def get_version(name, conf, callback):
  repo = conf.get('gems') or name
  url = GEMS_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_gems_done, name, callback))

def _gems_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data[0]['number']
  callback(name, version)
