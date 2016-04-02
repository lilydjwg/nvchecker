import os
import json
from functools import partial

from pkg_resources import parse_version
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

try:
  import pyalpm
  def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
      def __init__(self, obj, *args):
        self.obj = obj
      def __lt__(self, other):
        return mycmp(self.obj, other.obj) < 0
      def __gt__(self, other):
        return mycmp(self.obj, other.obj) > 0
      def __eq__(self, other):
        return mycmp(self.obj, other.obj) == 0
      def __le__(self, other):
        return mycmp(self.obj, other.obj) <= 0
      def __ge__(self, other):
        return mycmp(self.obj, other.obj) >= 0
      def __ne__(self, other):
        return mycmp(self.obj, other.obj) != 0
  vercmp = cmp_to_key(pyalpm.vercmp)
except ImportError:
  vercmp = None

GITHUB_URL = 'https://api.github.com/repos/%s/commits?sha=%s'
GITHUB_LATEST_RELEASE = 'https://api.github.com/repos/%s/releases/latest'
GITHUB_MAX_TAG = 'https://api.github.com/repos/%s/tags'

def get_version(name, conf, callback):
  repo = conf.get('github')
  br = conf.get('branch', 'master')
  use_latest_release = conf.getboolean('use_latest_release', False)
  use_max_tag = conf.getboolean('use_max_tag', False)
  ignored_tags = conf.get("ignored_tags", "").split()
  sort_version_key = {"parse_version": parse_version, "vercmp": vercmp}[conf.get("sort_version_key", "parse_version")]
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
                          callback=partial(_github_done, name, use_latest_release, use_max_tag, ignored_tags, sort_version_key, callback))

def _github_done(name, use_latest_release, use_max_tag, ignored_tags, sort_version_key, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  if use_latest_release:
    version = data['tag_name']
  elif use_max_tag:
    data = [tag["name"] for tag in data if tag["name"] not in ignored_tags]
    data.sort(key=sort_version_key)
    version = data[-1]
  else:
    # YYYYMMDD.HHMMSS
    version = data[0]['commit']['committer']['date'] \
        .rstrip('Z').replace('-', '').replace(':', '').replace('T', '.')
  callback(name, version)
