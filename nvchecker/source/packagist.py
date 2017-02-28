# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from .simple_json import simple_json

PACKAGIST_URL = 'https://packagist.org/packages/%s.json'

def _version_from_json(data):
  data = {version: details for version, details in data["package"]['versions'].items() if version != "dev-master"}

  if len(data):
    return max(data, key=lambda version: data[version]["time"])

get_version = simple_json(
  PACKAGIST_URL,
  'packagist',
  _version_from_json,
)
