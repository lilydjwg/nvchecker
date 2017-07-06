# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import logging
from importlib import import_module

logger = logging.getLogger(__name__)
handler_precedence = (
  'github', 'aur', 'pypi', 'archpkg', 'debianpkg', 'ubuntupkg',
  'gems', 'pacman',
  'cmd', 'bitbucket', 'regex', 'manual', 'vcs',
  'cratesio', 'npm', 'hackage', 'cpan', 'gitlab', 'packagist'
)

async def get_version(name, conf):
  for key in handler_precedence:
    if key in conf:
      func = import_module('.source.' + key, __package__).get_version
      return await func(name, conf)
  else:
    logger.error('%s: no idea to get version info.', name)
    return name, None
