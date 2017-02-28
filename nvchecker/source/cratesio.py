# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from ..sortversion import sort_version_keys

API_URL = 'https://crates.io/api/v1/crates/%s'

def get_version(name, conf, callback):
  name = conf.get('cratesio') or name
  request = HTTPRequest(API_URL % name, user_agent='lilydjwg/nvchecker')
  AsyncHTTPClient().fetch(
    request,
    callback = partial(_cratesio_done, name, callback),
  )

def _cratesio_done(name, callback, res):
  data = json.loads(res.body.decode('utf-8'))
  version = [v['num'] for v in data['versions'] if not v['yanked']][0]
  callback(name, version)
