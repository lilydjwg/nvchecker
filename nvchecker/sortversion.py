# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

'''
Sort versions using packaging.version, pkg_resource.parse_version, or pyalpm.vercmp
'''

__all__ = ["sort_version_keys"]

from functools import cmp_to_key

def sort_version_keys(method: str):
  if method == "packaging":
    from packaging import version
    return version.parse
  elif method == "parse_version":
    from pkg_resources import parse_version
    return parse_version
  elif method == "vercmp":
    import pyalpm
    return cmp_to_key(pyalpm.vercmp)
  else:
    raise NotImplementedError(f"Unsupported method {method} specified!")
