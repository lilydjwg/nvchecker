# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import re
from importlib import import_module

import structlog

from .sortversion import sort_version_keys

logger = structlog.get_logger(logger_name=__name__)

handler_precedence = (
  'github', 'aur', 'pypi', 'archpkg', 'debianpkg', 'ubuntupkg',
  'gems', 'pacman',
  'cmd', 'bitbucket', 'regex', 'manual', 'vcs',
  'cratesio', 'npm', 'hackage', 'cpan', 'gitlab', 'packagist',
  'repology', 'anitya', 'android_sdk',
)

def substitute_version(version, name, conf):
  '''
  Substitute the version string via defined rules in the configuration file.
  See README.rst#global-options for details.
  '''
  prefix = conf.get('prefix')
  if prefix:
    if version.startswith(prefix):
      version = version[len(prefix):]
    return version

  from_pattern = conf.get('from_pattern')
  if from_pattern:
    to_pattern = conf.get('to_pattern')
    if not to_pattern:
      raise ValueError('%s: from_pattern exists but to_pattern doesn\'t', name)

    return re.sub(from_pattern, to_pattern, version)

  # No substitution rules found. Just return the original version string.
  return version

def apply_list_options(versions, conf):
  pattern = conf.get('include_regex')
  if pattern:
    pattern = re.compile(pattern)
    versions = [x for x in versions
                if pattern.fullmatch(x)]

  pattern = conf.get('exclude_regex')
  if pattern:
    pattern = re.compile(pattern)
    versions = [x for x in versions
                if not pattern.fullmatch(x)]

  ignored = set(conf.get('ignored', '').split())
  if ignored:
    versions = [x for x in versions if x not in ignored]

  if not versions:
    return

  sort_version_key = sort_version_keys[
    conf.get("sort_version_key", "parse_version")]
  versions.sort(key=sort_version_key)

  return versions[-1]

_cache = {}

async def get_version(name, conf, **kwargs):
  for key in handler_precedence:
    if key in conf:
      mod = import_module('.source.' + key, __package__)
      func = mod.get_version
      get_cacheable_conf = getattr(mod, 'get_cacheable_conf', lambda name, conf: conf)
      break
  else:
    logger.error('no idea to get version info.', name=name)
    return

  cacheable_conf = get_cacheable_conf(name, conf)
  cache_key = tuple(sorted(cacheable_conf.items()))
  if cache_key in _cache:
    version = _cache[cache_key]
    logger.debug('cache hit', name=name,
                 cache_key=cache_key, cached=version)
    return version

  version = await func(name, conf, **kwargs)

  if isinstance(version, list):
    version = apply_list_options(version, conf)

  if version:
    version = version.replace('\n', ' ')
    try:
      version = substitute_version(version, name, conf)
    except (ValueError, re.error):
      logger.exception('error occurred in version substitutions', name=name)

  if version is not None:
    _cache[cache_key] = version

  return version
