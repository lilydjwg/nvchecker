#!/usr/bin/env python3
# vim:fileencoding=utf-8

import os
import sys
import configparser
import logging
import argparse
from functools import partial

from pkg_resources import parse_version
from tornado.ioloop import IOLoop

from .lib import notify

from .get_version import get_version
from . import util

logger = logging.getLogger(__name__)
notifications = []
g_counter = 0
g_oldver = {}
g_curver = {}

def task_inc():
  global g_counter
  g_counter += 1

def task_dec():
  global g_counter
  g_counter -= 1
  if g_counter == 0:
    IOLoop.instance().stop()
    write_verfile()

def load_config(*files):
  config = configparser.ConfigParser(
    dict_type=dict, allow_no_value=True
  )
  for file in files:
    with open(file) as f:
      config.read_file(f)

  return config

def load_oldverfile(file):
  v = {}
  with open(file) as f:
    for l in f:
      name, ver = [x.strip() for x in l.split(':', 1)]
      v[name] = ver
  return v

def write_verfile():
  if not args.newver:
    return

  with open(args.newver, 'w') as f:
    # sort using only alphanums, as done by the sort command, and needed by
    # comm command
    for item in sorted(g_curver.items(), key=lambda i: (''.join(filter(str.isalnum, i[0])), i[1])):
      print('%s: %s' % item, file=f)

def print_version_update(name, version):
  oldver = g_oldver.get(name, None)
  if not oldver or parse_version(oldver) < parse_version(version):
    logger.info('%s: updated version %s', name, version)
    _updated(name, version)
  else:
    logger.info('%s: current version %s', name, version)
  task_dec()

def _updated(name, version):
  g_curver[name] = version

  if args.notify:
    msg = '%s updated to version %s' % (name, version)
    notifications.append(msg)
    notify.update('nvchecker', '\n'.join(notifications))

def get_versions(config):
  task_inc()
  for name in config.sections():
    task_inc()
    get_version(name, config[name], print_version_update)
  task_dec()

def main():
  global args

  parser = argparse.ArgumentParser(description='New version checker for software')
  parser.add_argument('files', metavar='FILE', nargs='*',
                      help='software version source files')
  parser.add_argument('-n', '--notify', action='store_true', default=False,
                      help='show desktop notifications when a new version is available')
  util.add_common_arguments(parser)

  args = parser.parse_args()
  if util.process_common_arguments(args):
    return

  if not args.files:
    return

  def run_test():
    config = load_config(*args.files)
    if args.oldver:
      g_oldver.update(load_oldverfile(args.oldver))
      g_curver.update(g_oldver)
    get_versions(config)

  ioloop = IOLoop.instance()
  ioloop.add_callback(run_test)
  ioloop.start()

if __name__ == '__main__':
  main()
