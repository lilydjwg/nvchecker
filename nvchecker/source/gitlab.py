# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import json
from functools import partial
import logging
import urllib.parse

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from ..sortversion import sort_version_keys

GITLAB_URL = 'https://%s/api/v3/projects/%s/repository/commits?ref_name=%s'
GITLAB_MAX_TAG = 'https://%s/api/v3/projects/%s/repository/tags'

logger = logging.getLogger(__name__)

def get_version(name, conf, callback):
  repo = urllib.parse.quote_plus(conf.get('gitlab'))
  br = conf.get('branch', 'master')
  host = conf.get('host', "gitlab.com")
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  sort_version_key = sort_version_keys[conf.get("sort_version_key", "parse_version")]

  env_name = "NVCHECKER_GITLAB_TOKEN_" + host.upper().replace(".", "_").replace("/", "_")
  token = conf.get('token', os.environ.get(env_name, None))
  if token is None:
    logger.error('%s: No gitlab token specified.', name)
    callback(name, None)
    return

  if use_max_tag:
    url = GITLAB_MAX_TAG % (host, repo)
  else:
    url = GITLAB_URL % (host, repo, br)

  headers = {"PRIVATE-TOKEN": token}
  request = HTTPRequest(url, headers=headers, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(request,
                          callback=partial(_gitlab_done, name, use_max_tag, ignored_tags, sort_version_key, callback))

def _gitlab_done(name, use_max_tag, ignored_tags, sort_version_key, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  if use_max_tag:
    data = [tag["name"] for tag in data if tag["name"] not in ignored_tags]
    data.sort(key=sort_version_key)
    version = data[-1]
  else:
    version = data[0]['created_at'].split('T', 1)[0].replace('-', '')
  callback(name, version)
