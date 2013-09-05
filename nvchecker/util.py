# vim: se sw=2:

import os
import sys
import logging

from .lib import nicelogger

from . import __version__

_DEFAULT_CONFIG = os.path.expanduser('~/.nvcheckerrc')

def add_common_arguments(parser):
  parser.add_argument('-i', '--oldver',
                      help='read an existing version record file')
  parser.add_argument('-o', '--newver',
                      help='write a new version record file')
  parser.add_argument('-c', metavar='CONFIG_FILE', default=_DEFAULT_CONFIG,
                      help='specify the nvcheckerrc file to use')
  parser.add_argument('-l', '--logging',
                      choices=('debug', 'info', 'warning', 'error'), default='info',
                      help='logging level (default: info)')
  parser.add_argument('-V', '--version', action='store_true',
                      help='show version and exit')

def _get_rcargs():
  args = sys.argv[1:]
  args.reverse()
  it = iter(args)

  try:
    f = next(it)
    while True:
      j = next(it)
      if j == '-c':
        break
      f = j
  except StopIteration:
    if os.path.exists(_DEFAULT_CONFIG):
      f = _DEFAULT_CONFIG
    else:
      return []

  return [os.path.expandvars(os.path.expanduser(x))
          for x in open(f, 'r').read().split()]

def parse_args(parser):
  args = _get_rcargs()
  args += sys.argv[1:]
  return parser.parse_args(args)

def process_common_arguments(args):
  '''return True if should stop'''
  nicelogger.enable_pretty_logging(getattr(logging, args.logging.upper()))

  if args.version:
    progname = os.path.basename(sys.argv[0])
    print('%s v%s' % (progname, __version__))
    return True

def safe_overwrite(fname, data, *, method='write', mode='w', encoding=None):
  # FIXME: directory has no read perm
  # FIXME: symlinks and hard links
  tmpname = fname + '.tmp'
  # if not using "with", write can fail without exception
  with open(tmpname, mode, encoding=encoding) as f:
    getattr(f, method)(data)
  # if the above write failed (because disk is full etc), the old data should be kept
  os.rename(tmpname, fname)

def read_verfile(file):
  v = {}
  with open(file) as f:
    for l in f:
      name, ver = [x.strip() for x in l.split(':', 1)]
      v[name] = ver
  return v

def write_verfile(file, versions):
  # sort using only alphanums, as done by the sort command, and needed by
  # comm command
  data = ['%s: %s\n' % item
          for item in sorted(versions.items(), key=lambda i: (''.join(filter(str.isalnum, i[0])), i[1]))]
  safe_overwrite(file, data, method='writelines')

