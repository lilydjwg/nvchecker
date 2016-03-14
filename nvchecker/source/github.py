import os
import json
from functools import partial

from pkg_resources import parse_version
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

GITHUB_URL = 'https://api.github.com/repos/%s/commits?sha=%s'
GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/%s/releases/latest'
GITHUB_MAX_TAG = 'https://api.github.com/repos/%s/tags'

def get_version(name, conf, callback):
  repo = conf.get('github')
  br = conf.get('branch', 'master')
  use_latest_release = conf.getboolean('use_latest_release', False)
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  if use_latest_release:
    url = GITHUB_LATEST_RELEASE % repo
  elif use_max_tag:
    url = GITHUB_MAX_TAG % repo
  else:
    url = GITHUB_URL % (repo, br)
  headers = {'Accept': "application/vnd.github.quicksilver-preview+json"}
  if 'NVCHECKER_GITHUB_TOKEN' in os.environ:
    headers['Authorization'] = 'token %s' % os.environ['NVCHECKER_GITHUB_TOKEN']
  request = HTTPRequest(url, headers=headers, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(request,
                          callback=partial(_github_done, name, use_latest_release, use_max_tag, ignored_tags, callback))

def _github_done(name, use_latest_release, use_max_tag, ignored_tags, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  if use_latest_release:
    version = data['tag_name']
  elif use_max_tag:
    data = [tag["name"] for tag in data if tag["name"] not in ignored_tags]
    data.sort(key=parse_version)
    version = data[-1]
  else:
    # YYYYMMDD.HHMMSS
    version = data[0]['commit']['committer']['date'] \
        .rstrip('Z').replace('-', '').replace(':', '').replace('T', '.')
  callback(name, version)
