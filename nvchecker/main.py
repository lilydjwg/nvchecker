#!/usr/bin/env python3
# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import argparse
import asyncio

import structlog

from .lib import notify
from . import core

logger = structlog.get_logger(logger_name=__name__)

notifications = []
args = None

class Source(core.Source):
  def on_update(self, name, version, oldver):
    if args.notify:
      msg = '%s updated to version %s' % (name, version)
      notifications.append(msg)
      notify.update('nvchecker', '\n'.join(notifications))

def main():
  global args

  parser = argparse.ArgumentParser(description='New version checker for software')
  parser.add_argument('-n', '--notify', action='store_true', default=False,
                      help='show desktop notifications when a new version is available')
  parser.add_argument('-t', '--tries', default=1, type=int, metavar='N',
                      help='try N times when errors occur')
  core.add_common_arguments(parser)
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  if not args.file:
    return

  s = Source(args.file, args.tries)

  ioloop = asyncio.get_event_loop()
  ioloop.run_until_complete(s.check())

if __name__ == '__main__':
  main()
