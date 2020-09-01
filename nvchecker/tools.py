# vim: se sw=2:
# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import sys
import argparse
import structlog

from . import core

logger = structlog.get_logger(logger_name=__name__)

def take() -> None:
  parser = argparse.ArgumentParser(description='update version records of nvchecker')
  core.add_common_arguments(parser)
  parser.add_argument('--all', action='store_true',
                      help='take all updates')
  parser.add_argument('--ignore-nonexistent', action='store_true',
                      help='ignore nonexistent names')
  parser.add_argument('names', metavar='NAME', nargs='*',
                      help='software name to be updated')
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  opt = core.load_file(args.file, use_keymanager=False)[1]
  if opt.ver_files is None:
    logger.critical(
      "doesn't have 'oldver' and 'newver' set.",
      source=args.file,
    )
    sys.exit(2)
  else:
    oldverf = opt.ver_files[0]
    newverf = opt.ver_files[1]

  oldvers = core.read_verfile(oldverf)
  newvers = core.read_verfile(newverf)

  if args.all:
    oldvers.update(newvers)
  else:
    for name in args.names:
      try:
        oldvers[name] = newvers[name]
      except KeyError:
        if args.ignore_nonexistent:
          logger.warning('nonexistent in newver, ignored', name=name)
          continue

        logger.critical(
          "doesn't exist in 'newver' set.", name=name,
        )
        sys.exit(2)

  try:
    oldverf.rename(
      oldverf.with_name(oldverf.name + '~'),
    )
  except FileNotFoundError:
    pass
  core.write_verfile(oldverf, oldvers)

def cmp() -> None:
  parser = argparse.ArgumentParser(description='compare version records of nvchecker')
  core.add_common_arguments(parser)
  parser.add_argument('-q', '--quiet', action='store_true',
                      help="Quiet mode, output only the names.")
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  opt = core.load_file(args.file, use_keymanager=False)[1]
  if opt.ver_files is None:
    logger.critical(
      "doesn't have 'oldver' and 'newver' set.",
      source=args.file,
    )
    sys.exit(2)
  else:
    oldverf = opt.ver_files[0]
    newverf = opt.ver_files[1]

  oldvers = core.read_verfile(oldverf)
  newvers = core.read_verfile(newverf)
  for name, newver in sorted(newvers.items()):
    oldver = oldvers.get(name, None)
    if oldver != newver:
      if args.quiet:
        print(name)
      else:
        print('%s %s -> %s' % (name, oldver, newver))
