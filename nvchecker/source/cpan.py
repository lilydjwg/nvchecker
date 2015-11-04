import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient

# Using metacpan
CPAN_URL = 'https://api.metacpan.org/release/%s'

def get_version(name, conf, callback):
  repo = conf.get('cpan') or name
  url = CPAN_URL % repo
  AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                          callback=partial(_cpan_done, name, callback))

def _cpan_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['version']
  callback(name, version)
