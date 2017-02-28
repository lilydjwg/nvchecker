# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from .simple_json import simple_json

PYPI_URL = 'https://pypi.python.org/pypi/%s/json'

def _version_from_json(data):
  return data['info']['version']

get_version = simple_json(
  PYPI_URL,
  'pypi',
  _version_from_json,
)
