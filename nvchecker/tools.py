# vim: se sw=2:

import sys
import argparse

from . import util

def take():
  parser = argparse.ArgumentParser(description='update version records of nvchecker')
  parser.add_argument('names', metavar='NAME', nargs='*',
                      help='software name to be updated')
  util.add_common_arguments(parser)

  args = util.parse_args(parser)
  if util.process_common_arguments(args):
    return

  if not args.oldver or not args.newver:
    sys.exit('You must specify old and new version records so that I can update.')

  oldvers = util.read_verfile(args.oldver)
  newvers = util.read_verfile(args.newver)

  for name in args.names:
    oldvers[name] = newvers[name]

  util.write_verfile(args.oldver, oldvers)
