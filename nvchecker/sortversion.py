# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

'''
Sort versions using pkg_resource.parse_version or pyalpm.vercmp
'''

__all__ = ["sort_version_keys"]

import logging

from functools import cmp_to_key

logger = logging.getLogger(__name__)

from pkg_resources import parse_version
try:
  import pyalpm
  vercmp = cmp_to_key(pyalpm.vercmp)
except ImportError:
  def vercmp(k):
    raise NotImplementedError("Using vercmp but pyalpm can not be imported!")

sort_version_keys = {"parse_version": parse_version, "vercmp": vercmp}

if __name__ == '__main__':
  assert(parse_version("v6.0") < parse_version("6.1"))
  assert(parse_version("v6.0") > parse_version("v6.1-stable"))
  assert(vercmp("v6.0") < vercmp("v6.1-stable"))
