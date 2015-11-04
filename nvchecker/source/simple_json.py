import json
from functools import partial

from tornado.httpclient import AsyncHTTPClient

def simple_json(urlpat, confkey, version_from_json):

  def get_version(name, conf, callback):
    repo = conf.get(confkey) or name
    url = urlpat % repo
    AsyncHTTPClient().fetch(url, user_agent='lilydjwg/nvchecker',
                            callback=partial(_json_done, name, callback))

  def _json_done(name, callback, res):
    data = json.loads(res.body.decode('utf-8'))
    version = version_from_json(data)
    callback(name, version)

  return get_version
