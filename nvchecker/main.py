#!/usr/bin/env python3
# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import logging
import argparse

from tornado.ioloop import IOLoop

from .lib import notify
from . import core

logger = logging.getLogger(__name__)
notifications = []
args = None

class Source(core.Source):
  def on_update(self, name, version, oldver):
    if args.notify:
      msg = '%s updated to version %s' % (name, version)
      notifications.append(msg)
      notify.update('nvchecker', '\n'.join(notifications))

  def on_finish(self):
    IOLoop.instance().stop()

def main():
  global args

  parser = argparse.ArgumentParser(description='New version checker for software')
  parser.add_argument('-n', '--notify', action='store_true', default=False,
                      help='show desktop notifications when a new version is available')
  core.add_common_arguments(parser)
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  if not args.file:
    return
  s = Source(args.file)

  ioloop = IOLoop.instance()
  ioloop.add_callback(s.check)
  ioloop.start()

if __name__ == '__main__':
  main()
