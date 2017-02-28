# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from .simple_json import simple_json

HACKAGE_URL = 'https://hackage.haskell.org/package/%s/preferred.json'

def _version_from_json(data):
  return data['normal-version'][0]

get_version = simple_json(
  HACKAGE_URL,
  'hackage',
  _version_from_json,
)
