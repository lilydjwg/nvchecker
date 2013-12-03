# vim: se sw=2:

import sys
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
    logger.error(
      "%s doesn't have both 'oldver' and 'newver' set, ignoring.", s
    )

  oldvers = core.read_verfile(s.oldver)
  newvers = core.read_verfile(s.newver)

  for name in args.names:
    oldvers[name] = newvers[name]

  core.write_verfile(s.oldver, oldvers)
