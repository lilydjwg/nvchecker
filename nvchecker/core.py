# vim: se sw=2:
# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import sys
import logging
import configparser
import asyncio

from .lib import nicelogger
from .get_version import get_version
from .source import session

from . import __version__

logger = logging.getLogger(__name__)

def add_common_arguments(parser):
  parser.add_argument('-l', '--logging',
                      choices=('debug', 'info', 'warning', 'error'), default='info',
                      help='logging level (default: info)')
  parser.add_argument('-V', '--version', action='store_true',
                      help='show version and exit')
  parser.add_argument('file', metavar='FILE', nargs='?', type=open,
                      help='software version source file')

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
    # see also: https://thunk.org/tytso/blog/2009/03/15/dont-fear-the-fsync/
    f.flush()
    os.fsync(f.fileno())
  # if the above write failed (because disk is full etc), the old data should be kept
  os.rename(tmpname, fname)

def read_verfile(file):
  v = {}
  try:
    with open(file) as f:
      for l in f:
        name, ver = l.rstrip().split(None, 1)
        v[name] = ver
  except FileNotFoundError:
    pass
  return v

def write_verfile(file, versions):
  # sort using only alphanums, as done by the sort command, and needed by
  # comm command
  data = ['%s %s\n' % item
          for item in sorted(versions.items(), key=lambda i: (''.join(filter(str.isalnum, i[0])), i[1]))]
  safe_overwrite(file, data, method='writelines')

class Source:
  oldver = newver = None

  def __init__(self, file):
    self.config = config = configparser.ConfigParser(
      dict_type=dict, allow_no_value=True
    )
    self.name = file.name
    config.read_file(file)
    if '__config__' in config:
      c = config['__config__']

      if 'oldver' in c and 'newver' in c:
        d = os.path.dirname(file.name)
        self.oldver = os.path.expandvars(os.path.expanduser(
          os.path.join(d, c.get('oldver'))))
        self.newver = os.path.expandvars(os.path.expanduser(
          os.path.join(d, c.get('newver'))))

      self.max_concurrent = c.getint('max_concurrent', 20)
      session.nv_config = config["__config__"]

    else:
      self.max_concurrent = 20

  async def check(self):
    if self.oldver:
      self.oldvers = read_verfile(self.oldver)
    else:
      self.oldvers = {}
    self.curvers = self.oldvers.copy()

    futures = set()
    config = self.config
    for name in config.sections():
      if name == '__config__':
        continue
      conf = config[name]
      conf['oldver'] = self.oldvers.get(name, None)
      fu = asyncio.ensure_future(get_version(name, conf))
      fu.name = name
      futures.add(fu)

      if len(futures) >= self.max_concurrent:
        (done, futures) = await asyncio.wait(
          futures, return_when = asyncio.FIRST_COMPLETED)
        for fu in done:
          self.future_done(fu)

    if futures:
      (done, _) = await asyncio.wait(futures)
      for fu in done:
        self.future_done(fu)

    if self.newver:
      write_verfile(self.newver, self.curvers)

  def future_done(self, fu):
    name = fu.name
    try:
      version = fu.result()
      if version is not None:
        self.print_version_update(name, version)
    except Exception:
      logger.exception('unexpected error happened with %s', name)

  def print_version_update(self, name, version):
    oldver = self.oldvers.get(name, None)
    if not oldver or oldver != version:
      logger.info('%s updated to %s', name, version)
      self.curvers[name] = version
      self.on_update(name, version, oldver)
    else:
      logger.debug('%s current %s', name, version)

  def on_update(self, name, version, oldver):
    pass

  def __repr__(self):
    return '<Source from %r>' % self.name
