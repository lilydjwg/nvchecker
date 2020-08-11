# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from importlib import import_module

import structlog

logger = structlog.get_logger(logger_name=__name__)

_handler_precedence = (
  'github', 'aur', 'pypi', 'archpkg', 'debianpkg', 'ubuntupkg',
  'gems', 'pacman',
  'cmd', 'bitbucket', 'regex', 'manual', 'vcs',
  'cratesio', 'npm', 'hackage', 'cpan', 'gitlab', 'packagist',
  'repology', 'anitya', 'android_sdk', 'sparkle', 'gitea'
)

_Task = namedtuple('_Task', 'batch_mode main args names')

class Dispatcher:
  def __init__(self):
    self.futures = []
    self.mods = {}
    self.tasks_dedupe = {}

  def add_task(self, name, conf, **kwargs):
    for key in _handler_precedence:
      if key not in conf:
        continue

      value = self.mods.get(key)
      if not value:
        mod = import_module(
          '.source.' + key, __package__)
        batch_mode = getattr(mod, 'BATCH_MODE', False)
        if batch_mode:
          main = mod.Batcher()
        else:
          main = mod.get_version
        get_cacheable_conf = getattr(mod, 'get_cacheable_conf', lambda name, conf: conf)
        self.mods[key] = batch_mode, main, get_cacheable_conf
      else:
        batch_mode, main, get_cacheable_conf = value

      cacheable_conf = get_cacheable_conf(name, conf)
      cache_key = tuple(sorted(cacheable_conf.items()))
      task = self.tasks_dedupe.get(cache_key)
      if task is None:
        self.tasks_dedupe[cache_key] = _Task(
          batch_mode, main, (cacheable_conf, kwargs), [name])
      else:
        task.names.append(name)

    else:
      logger.error(
        'no idea to get version info.', name=name)

