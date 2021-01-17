# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

'''
Sort versions using pkg_resource.parse_version or pyalpm.vercmp
'''

__all__ = ["sort_version_keys"]

from functools import cmp_to_key

from pkg_resources import parse_version
try:
  import pyalpm
  vercmp = cmp_to_key(pyalpm.vercmp)
  vercmp_available = True
except ImportError:
  def vercmp(k):
    raise NotImplementedError("Using vercmp but pyalpm can not be imported!")
  vercmp_available = False

sort_version_keys = {"parse_version": parse_version, "vercmp": vercmp}
