# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient

from .base import pycurl

def simple_json(urlpat, confkey, version_from_json):

  def get_version(name, conf, callback):
    repo = conf.get(confkey) or name
    url = urlpat % repo
    kwargs = {}
    if conf.get('proxy'):
      if pycurl:
        kwargs['proxy_host'] = "".join(conf['proxy'].split(':')[:-1])
        kwargs['proxy_port'] = int(conf['proxy'].split(':')[-1])
      else:
        logger.warn('%s: proxy set but not used because pycurl is unavailable.', name)

    AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                            callback=partial(_json_done, name, callback), **kwargs)

  def _json_done(name, callback, res):
    data = json.loads(res.body.decode('utf-8'))
    version = version_from_json(data)
    callback(name, version)

  return get_version
