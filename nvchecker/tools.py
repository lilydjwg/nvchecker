# vim: se sw=2:
# MIT licensed
# Copyright (c) 2013-2024 lilydjwg <lilydjwg@gmail.com>, et al.

import sys
import argparse
import shutil
import structlog
import json
import os.path

from . import core
from .util import RichResult

logger = structlog.get_logger(logger_name=__name__)

def take() -> None:
  parser = argparse.ArgumentParser(description='update version records of nvchecker')
  core.add_common_arguments(parser)
  parser.add_argument('--all', action='store_true',
                      help='take all updates')
  parser.add_argument('--ignore-nonexistent', action='store_true',
                      help='ignore nonexistent names')
  parser.add_argument('names', metavar='NAME', nargs='*',
                      help='software name to be updated. use NAME=VERSION to update '
                           'to a specific version instead of the new version.')
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
    name: str
    for name in args.names:
      if "=" in name:
        name, newver = name.split("=")
        oldvers[name] = RichResult(version=newver)
      else:
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
    if os.path.islink(oldverf):
      shutil.copy(oldverf, oldverf.with_name(oldverf.name + '~'))
    else:
      oldverf.rename(
        oldverf.with_name(oldverf.name + '~'),
      )
  except FileNotFoundError:
    pass
  core.write_verfile(oldverf, oldvers)

def cmp() -> None:
  parser = argparse.ArgumentParser(description='compare version records of nvchecker')
  core.add_common_arguments(parser)
  parser.add_argument('-j', '--json', action='store_true',
                      help='Output JSON array of dictionaries with {name, newver, oldver, [delta]} '
                           '(or array of names if --quiet)')
  parser.add_argument('-q', '--quiet', action='store_true',
                      help="Quiet mode, output only the names.")
  parser.add_argument('-a', '--all', action='store_true',
                      help="Include unchanged versions.")
  parser.add_argument('-s', '--sort',
                      choices=('parse_version', 'vercmp', 'awesomeversion', 'none'),
                      default='parse_version',
                      help='Version compare method to backwards the arrow '
                           '(default: parse_version)')
  parser.add_argument('-n', '--newer', action='store_true',
                      help='Shows only the newer ones according to --sort.')
  parser.add_argument('--exit-status', action='store_true',
                      help="exit with status 4 if there are updates")
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

  oldvers = {k: v.version for k, v in core.read_verfile(oldverf).items()}
  newvers = {k: v.version for k, v in core.read_verfile(newverf).items()}

  differences = []

  for name, newver in sorted(newvers.items()):  # accumulate differences
    oldver = oldvers.get(name, None)

    diff = {
      'name': name,
      'oldver': oldver,
      'newver': newver
    }

    if oldver is not None and newver is not None:
      if oldver == newver:
        diff['delta'] = 'equal'

      elif args.sort == "none":
        diff['delta'] = 'new'  # assume it's a new version if we're not comparing

      else:
        from .sortversion import sort_version_keys
        version = sort_version_keys[args.sort]

        if version(oldver) > version(newver): # type: ignore
          if args.newer:
            continue  # don't store this diff
          diff['delta'] = 'old'
        else:
          diff['delta'] = 'new'

    elif oldver is None:
      diff['delta'] = 'added'

    elif newver is None:
      if args.newer:
        continue  # don't store this diff
      diff['delta'] = 'gone'

    if args.all or diff['delta'] != 'equal':
      differences.append(diff)

  if args.json:
    if args.quiet:
      print(json.dumps([diff['name'] for diff in differences], separators=(',', ':')))
    else:
      print(json.dumps(differences, sort_keys=True, separators=(',', ':')))

  elif args.quiet:
    for diff in differences:
      print(diff['name'])

  else:
    from .lib.nicelogger import Colors, support_color
    c = Colors(support_color(sys.stdout))

    diffstyles = {
      'new': {
        'symbol': '->',
        'oldc': c.red
      },
      'old': {
        'symbol': f'{c.red}<-{c.normal}',
        'oldc': c.red
      },
      'added': {
        'symbol': '++',
        'oldc': c.red
      },
      'gone': {
        'symbol': f'{c.red}--{c.normal}',
        'oldc': c.green
      },
      'equal': {
        'symbol': '==',
        'oldc': c.green
      }
    }

    for diff in differences:
      style = diffstyles[diff.get('delta', 'equal')] # type: ignore # mypy has issues with this line

      print(f'{diff["name"]} {style["oldc"]}{diff["oldver"]}{c.normal} {style["symbol"]} {c.green}{diff["newver"]}{c.normal}')

  if args.exit_status and any(
    diff.get('delta') != 'equal' for diff in differences
  ):
    sys.exit(4)
