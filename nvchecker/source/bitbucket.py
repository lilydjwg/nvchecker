# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from ..sortversion import sort_version_keys

# doc: https://confluence.atlassian.com/display/BITBUCKET/commits+or+commit+Resource
BITBUCKET_URL = 'https://bitbucket.org/api/2.0/repositories/%s/commits/%s'
BITBUCKET_MAX_TAG = 'https://bitbucket.org/api/1.0/repositories/%s/tags'

def get_version(name, conf, callback):
  repo = conf.get('bitbucket')
  br = conf.get('branch', '')
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  sort_version_key = sort_version_keys[conf.get("sort_version_key", "parse_version")]
  if use_max_tag:
    url = BITBUCKET_MAX_TAG % repo
  else:
    url = BITBUCKET_URL % (repo, br)
  request = HTTPRequest(url, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(request,
                          callback=partial(_bitbucket_done, name, use_max_tag, ignored_tags, sort_version_key, callback))

def _bitbucket_done(name, use_max_tag, ignored_tags, sort_version_key, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  if use_max_tag:
    data = [tag for tag in data if tag not in ignored_tags]
    data.sort(key=sort_version_key)
    version = data[-1]
  else:
    version = data['values'][0]['date'].split('T', 1)[0].replace('-', '')
  callback(name, version)
