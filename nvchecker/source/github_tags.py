import os
import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

GITHUB_URL = 'https://api.github.com/repos/%s/tags'

def get_version(name, conf, callback):
  repo = conf.get('github_tags')
  url = GITHUB_URL % (repo)
  headers = {'Accept': "application/vnd.github.quicksilver-preview+json"}
  if 'NVCHECKER_GITHUB_TOKEN' in os.environ:
      headers['Authorization'] = 'token %s' % os.environ['NVCHECKER_GITHUB_TOKEN']
  request = HTTPRequest(url, headers=headers, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(request,
                          callback=partial(_github_tags_done, name, callback))

def _github_tags_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = data[0]['name'].strip('v')
  callback(name, version)
