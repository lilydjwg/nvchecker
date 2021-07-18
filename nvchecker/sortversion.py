# MIT licensed
# Copyright (c) 2013-2021 lilydjwg <lilydjwg@gmail.com>, et al.

'''
Sort versions using deprecated pkg_resource / packaging.parse_version or pyalpm.vercmp
'''

__all__ = ["sort_version_keys"]

from .lib.packaging_version import parse as parse_version
try:
  import pyalpm
  from functools import cmp_to_key
  vercmp = cmp_to_key(pyalpm.vercmp)
  vercmp_available = True
except ImportError:
  def vercmp(k):
    raise NotImplementedError("Using vercmp but pyalpm can not be imported!")
  vercmp_available = False

sort_version_keys = {"parse_version": parse_version, "vercmp": vercmp}
