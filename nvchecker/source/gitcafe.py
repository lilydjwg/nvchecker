import os
import json
import re
from functools import partial

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

GITCAFE_URL = 'https://gitcafe.com/%s/commits/%s'
gitcafe_pattern = re.compile(r'datetime="([^"]*)"')

def get_version(name, conf, callback):
  repo = conf.get('gitcafe')
  br = conf.get('branch', 'master')
  url = GITCAFE_URL % (repo, br)
  headers = {'Accept': "text/html"}
  request = HTTPRequest(url, headers=headers, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(request, callback=partial(_gitcafe, name, callback))

def _gitcafe(name, callback, res):
  body = res.body.decode('utf-8')
  data = gitcafe_pattern.search(body).group(1)
  version = data.split('T', 1)[0].replace('-', '')
  callback(name, version)
