# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from .simple_json import simple_json

NPM_URL = 'https://registry.npmjs.org/%s'

def _version_from_json(data):
  return data['dist-tags']['latest']

get_version = simple_json(
  NPM_URL,
  'npm',
  _version_from_json,
)
