# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from .simple_json import simple_json

GEMS_URL = 'https://rubygems.org/api/v1/versions/%s.json'

def _version_from_json(data):
  return data[0]['number']

get_version = simple_json(
  GEMS_URL,
  'gems',
  _version_from_json,
)
