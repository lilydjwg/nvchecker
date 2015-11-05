import os
import json
from functools import partial

from pkg_resources import parse_version
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

# doc: https://confluence.atlassian.com/display/BITBUCKET/commits+or+commit+Resource
BITBUCKET_URL = 'https://bitbucket.org/api/2.0/repositories/%s/commits/%s'
BITBUCKET_MAX_TAG = 'https://bitbucket.org/api/1.0/repositories/%s/tags'

def get_version(name, conf, callback):
  repo = conf.get('bitbucket')
  br = conf.get('branch', '')
  use_max_tag = conf.getboolean('use_max_tag', False)
  if use_max_tag:
    url = BITBUCKET_MAX_TAG % repo
  else:
    url = BITBUCKET_URL % (repo, br)
  request = HTTPRequest(url, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(request,
                          callback=partial(_bitbucket_done, name, use_max_tag, callback))

def _bitbucket_done(name, use_max_tag, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  if use_max_tag:
    data = list(data)
    data.sort(key=parse_version)
    version = data[-1]
  else:
    version = data['values'][0]['date'].split('T', 1)[0].replace('-', '')
  callback(name, version)
