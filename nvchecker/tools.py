# vim: se sw=2:
# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import sys
import os
import argparse
import logging

from . import core

logger = logging.getLogger(__name__)

def take():
  parser = argparse.ArgumentParser(description='update version records of nvchecker')
  core.add_common_arguments(parser)
  parser.add_argument('names', metavar='NAME', nargs='*',
                      help='software name to be updated')
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  s = core.Source(args.file)
  if not s.oldver or not s.newver:
    logger.fatal(
      "%s doesn't have both 'oldver' and 'newver' set.", s
    )
    sys.exit(2)

  oldvers = core.read_verfile(s.oldver)
  newvers = core.read_verfile(s.newver)

  for name in args.names:
    oldvers[name] = newvers[name]

  try:
      os.rename(s.oldver, s.oldver + '~')
  except FileNotFoundError:
      pass
  core.write_verfile(s.oldver, oldvers)

def cmp():
  parser = argparse.ArgumentParser(description='compare version records of nvchecker')
  core.add_common_arguments(parser)
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  s = core.Source(args.file)
  oldvers = core.read_verfile(s.oldver) if s.oldver else {}
  newvers = core.read_verfile(s.newver)
  for name, newver in sorted(newvers.items()):
    oldver = oldvers.get(name, None)
    if oldver != newver:
      print('%s %s -> %s' % (name, oldver, newver))
