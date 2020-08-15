# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import os
import sys
import asyncio
from asyncio import Queue
import logging
import argparse
from typing import (
  TextIO, Tuple, NamedTuple, Optional, List, Union,
  cast, Dict, Awaitable, Sequence,
)
import types
from pathlib import Path
from importlib import import_module
import re
import contextvars

import structlog
import toml

from .lib import nicelogger
from . import slogconf
from .util import (
  Entry, Entries, KeyManager, RawResult, Result, VersData,
  FunctionWorker, GetVersionError,
)
from . import __version__
from .sortversion import sort_version_keys
from .ctxvars import tries as ctx_tries

logger = structlog.get_logger(logger_name=__name__)

def get_default_config() -> str:
  confdir = os.environ.get('XDG_CONFIG_DIR', os.path.expanduser('~/.config'))
  file = os.path.join(confdir, 'nvchecker/nvchecker.toml')
  return file

def add_common_arguments(parser: argparse.ArgumentParser) -> None:
  parser.add_argument('-l', '--logging',
                      choices=('debug', 'info', 'warning', 'error'), default='info',
                      help='logging level (default: info)')
  parser.add_argument('--logger', default='pretty',
                      choices=['pretty', 'json', 'both'],
                      help='select which logger to use')
  parser.add_argument('--json-log-fd', metavar='FD',
                      type=lambda fd: os.fdopen(int(fd), mode='w'),
                      help='specify fd to send json logs to. stdout by default')
  parser.add_argument('-V', '--version', action='store_true',
                      help='show version and exit')
  parser.add_argument('-c', '--file',
                      metavar='FILE', type=open,
                      help='software version configuration file [default: %s]' % get_default_config)

def process_common_arguments(args: argparse.Namespace) -> bool:
  '''return True if should stop'''
  processors = [
    slogconf.exc_info,
    slogconf.filter_exc,
  ]
  logger_factory = None

  if args.logger in ['pretty', 'both']:
    slogconf.fix_logging()
    nicelogger.enable_pretty_logging(
      getattr(logging, args.logging.upper()))
    processors.append(slogconf.stdlib_renderer)
    if args.logger == 'pretty':
      logger_factory=structlog.PrintLoggerFactory(
        file=open(os.devnull, 'w'),
      )
      processors.append(slogconf.null_renderer)
  if args.logger in ['json', 'both']:
    processors.extend([
      structlog.processors.format_exc_info,
      slogconf.json_renderer,
    ])

  if logger_factory is None:
    logfile = args.json_log_fd or sys.stdout
    logger_factory = structlog.PrintLoggerFactory(file=logfile)

  structlog.configure(
    processors = processors,
    logger_factory = logger_factory,
  )

  if args.version:
    progname = os.path.basename(sys.argv[0])
    print('%s v%s' % (progname, __version__))
    return True
  return False

def safe_overwrite(fname: str, data: Union[bytes, str], *,
                   method: str = 'write', mode: str = 'w', encoding: Optional[str] = None) -> None:
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

def read_verfile(file: Path) -> VersData:
  v = {}
  try:
    with open(file) as f:
      for l in f:
        name, ver = l.rstrip().split(None, 1)
        v[name] = ver
  except FileNotFoundError:
    pass
  return v

def write_verfile(file: Path, versions: VersData) -> None:
  # sort using only alphanums, as done by the sort command,
  # and needed by comm command
  data = ['%s %s\n' % item
          for item in sorted(versions.items(), key=lambda i: (''.join(filter(str.isalnum, i[0])), i[1]))]
  safe_overwrite(
    str(file), ''.join(data), method='writelines')

class Options(NamedTuple):
  ver_files: Optional[Tuple[Path, Path]]
  max_concurrency: int
  keymanager: KeyManager

def load_file(
  file: TextIO,
) -> Tuple[Entries, Options]:
  config = toml.load(file)
  ver_files: Optional[Tuple[Path, Path]] = None

  if '__config__' in config:
    c = config.pop('__config__')
    d = Path(file.name).parent

    if 'oldver' in c and 'newver' in c:
      oldver_s = os.path.expandvars(
        os.path.expanduser(c.get('oldver')))
      oldver = d / oldver_s
      newver_s = os.path.expandvars(
        os.path.expanduser(c.get('newver')))
      newver = d / newver_s
      ver_files = oldver, newver

    keyfile = c.get('keyfile')
    if keyfile:
      keyfile_s = os.path.expandvars(
        os.path.expanduser(c.get('keyfile')))
      keyfile = d / keyfile_s

    max_concurrency = c.get(
      'max_concurrency', 20)
    keymanager = KeyManager(keyfile)

  else:
    max_concurrency = 20
    keymanager = KeyManager(None)

  return cast(Entries, config), Options(
    ver_files, max_concurrency, keymanager)

def token_queue(maxsize: int) -> Queue[bool]:
  token_q: Queue[bool] = Queue(maxsize=maxsize)

  for _ in range(maxsize):
    token_q.put_nowait(True)

  return token_q

def dispatch(
  entries: Entries,
  token_q: Queue[bool],
  result_q: Queue[RawResult],
  keymanager: KeyManager,
  tries: int,
) -> List[asyncio.Future]:
  mods: Dict[str, Tuple[types.ModuleType, List]] = {}
  ctx_tries.set(tries)
  root_ctx = contextvars.copy_context()

  for name, entry in entries.items():
    source = entry.get('source', 'none')
    if source not in mods:
      mod = import_module('nvchecker_source.' + source)
      tasks: List[Tuple[str, Entry]] = []
      mods[source] = mod, tasks
    else:
      tasks = mods[source][1]
    tasks.append((name, entry))

  ret = []
  for mod, tasks in mods.values():
    if hasattr(mod, 'Worker'):
      worker_cls = mod.Worker # type: ignore
    else:
      worker_cls = FunctionWorker

    ctx = root_ctx.copy()
    worker = ctx.run(
      worker_cls,
      token_q, result_q, tasks, keymanager,
    )
    if worker_cls is FunctionWorker:
      func = mod.get_version # type: ignore
      ctx.run(worker.initialize, func)

    ret.append(ctx.run(worker.run))

  return ret

def substitute_version(
  version: str, conf: Entry,
) -> str:
  '''
  Substitute the version string via defined rules in the configuration file.
  See README.rst#global-options for details.
  '''
  prefix = conf.get('prefix')
  if prefix:
    if version.startswith(prefix):
      version = version[len(prefix):]
    return version

  from_pattern = conf.get('from_pattern')
  if from_pattern:
    to_pattern = conf.get('to_pattern')
    if not to_pattern:
      raise ValueError("from_pattern exists but to_pattern doesn't")

    return re.sub(from_pattern, to_pattern, version)

  # No substitution rules found. Just return the original version string.
  return version

def apply_list_options(
  versions: List[str], conf: Entry,
) -> Optional[str]:
  pattern = conf.get('include_regex')
  if pattern:
    re_pat = re.compile(pattern)
    versions = [x for x in versions
                if re_pat.fullmatch(x)]

  pattern = conf.get('exclude_regex')
  if pattern:
    re_pat = re.compile(pattern)
    versions = [x for x in versions
                if not re_pat.fullmatch(x)]

  ignored = set(conf.get('ignored', '').split())
  if ignored:
    versions = [x for x in versions if x not in ignored]

  if not versions:
    return None

  sort_version_key = sort_version_keys[
    conf.get("sort_version_key", "parse_version")]
  versions.sort(key=sort_version_key)

  return versions[-1]

def _process_result(r: RawResult) -> Optional[Result]:
  version = r.version
  conf = r.conf
  name = r.name

  if isinstance(version, GetVersionError):
    kw = version.kwargs
    kw['name'] = name
    logger.error(version.msg, **kw)
    return None
  elif isinstance(version, Exception):
    logger.error('unexpected error happened',
                  name=r.name, exc_info=r.version)
    return None
  elif isinstance(version, list):
    version_str = apply_list_options(version, conf)
  else:
    version_str = version

  if version_str:
    version_str = version_str.replace('\n', ' ')

    try:
      version_str = substitute_version(version_str, conf)
      return Result(name, version_str, conf)
    except (ValueError, re.error):
      logger.exception('error occurred in version substitutions', name=name)

  return None

def check_version_update(
  oldvers: VersData, name: str, version: str,
) -> Optional[str]:
  oldver = oldvers.get(name, None)
  if not oldver or oldver != version:
    logger.info('updated', name=name, version=version, old_version=oldver)
    return version
  else:
    logger.debug('up-to-date', name=name, version=version)
    return None

async def process_result(
  oldvers: VersData,
  result_q: Queue[RawResult],
) -> VersData:
  ret = {}
  try:
    while True:
      r = await result_q.get()
      r1 = _process_result(r)
      if r1 is None:
        continue
      v = check_version_update(
        oldvers, r1.name, r1.version)
      if v is not None:
        ret[r1.name] = v
  except asyncio.CancelledError:
    return ret

async def run_tasks(
  futures: Sequence[Awaitable[None]]
) -> None:
  for fu in asyncio.as_completed(futures):
    await fu
