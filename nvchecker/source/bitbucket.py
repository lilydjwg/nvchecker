import os
import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

# doc: https://confluence.atlassian.com/display/BITBUCKET/commits+or+commit+Resource
BITBUCKET_URL = 'https://bitbucket.org/api/2.0/repositories/%s/commits/%s'

def get_version(name, conf, callback):
  repo = conf.get('bitbucket')
  br = conf.get('branch', '')
  url = BITBUCKET_URL % (repo, br)
  request = HTTPRequest(url, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(request,
                          callback=partial(_bitbucket_done, name, callback))

def _bitbucket_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data['values'][0]['date'].split('T', 1)[0].replace('-', '')
  callback(name, version)
