# MIT licensed
# Copyright (c) 2013-2020, 2024 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import os
import sys
import asyncio
from asyncio import Queue
import logging
import argparse
from typing import (
  Tuple, NamedTuple, Optional, List, Union,
  cast, Dict, Awaitable, Sequence, Any,
  TYPE_CHECKING,
)
import types
from pathlib import Path
from importlib import import_module
import re
import contextvars
import json
import dataclasses

import structlog

if TYPE_CHECKING:
  import tomli as tomllib
else:
  try:
    import tomllib
  except ModuleNotFoundError:
    import tomli as tomllib

import platformdirs

from .lib import nicelogger
from . import slogconf
from .util import (
  Entry, Entries, KeyManager, RawResult, RichResult, ResultData,
  FunctionWorker, GetVersionError,
  FileLoadError, EntryWaiter,
)
from . import __version__
from .sortversion import sort_version_keys
from .ctxvars import tries as ctx_tries
from .ctxvars import entry_waiter as ctx_entry_waiter
from . import httpclient

logger = structlog.get_logger(logger_name=__name__)

def get_default_config() -> str:
  confdir = platformdirs.user_config_dir(appname='nvchecker')
  file = os.path.join(confdir, 'nvchecker.toml')
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
  default_config = get_default_config()
  parser.add_argument('-c', '--file',
                      metavar='FILE', type=str,
                      default=default_config,
                      help=f'software version configuration file [default: {default_config}]')

def process_common_arguments(args: argparse.Namespace) -> bool:
  '''return True if should stop'''
  processors = [
    slogconf.exc_info,
    slogconf.filter_exc,
    slogconf.filter_nones,
    slogconf.filter_taskname,
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
    print(f'{progname} v{__version__}')
    return True
  return False

def safe_overwrite(file: Path, data: Union[bytes, str], *,
                   method: str = 'write', mode: str = 'w', encoding: Optional[str] = None) -> None:
  # FIXME: directory has no read perm
  # FIXME: hard links
  resolved_path = file.resolve()
  tmpname = str(resolved_path) + '.tmp'
  # if not using "with", write can fail without exception
  with open(tmpname, mode, encoding=encoding) as f:
    getattr(f, method)(data)
    # see also: https://thunk.org/tytso/blog/2009/03/15/dont-fear-the-fsync/
    f.flush()
    os.fsync(f.fileno())
  # if the above write failed (because disk is full etc), the old data should be kept
  os.rename(tmpname, resolved_path)

def read_verfile(file: Path) -> ResultData:
  try:
    with open(file) as f:
      data = f.read()
  except FileNotFoundError:
    return {}

  try:
    v = json.loads(data)
  except json.decoder.JSONDecodeError:
    # old format
    v = {}
    for l in data.splitlines():
      name, ver = l.rstrip().split(None, 1)
      v[name] = ver

  if v.get('version') is None:
    v = {k: RichResult(version=a) for k, a in v.items()}
  elif v['version'] == 2:
    v = {k: RichResult(**a) for k, a in v['data'].items()}
  else:
    raise Exception('unknown verfile version', v['version'])

  return v

def write_verfile(file: Path, versions: ResultData) -> None:
  d = {
    'version': 2,
    # sort and indent to make it friendly to human and git
    'data': dict(sorted(versions.items())),
  }
  data = json.dumps(
    d,
    indent = 2,
    ensure_ascii = False,
    default = json_encode,
  ) + '\n'
  safe_overwrite(file, data)

def json_encode(obj):
  if isinstance(obj, RichResult):
    d = {k: v for k, v in dataclasses.asdict(obj).items() if v is not None}
    return d
  raise TypeError(obj)

class Options(NamedTuple):
  ver_files: Optional[Tuple[Path, Path]]
  max_concurrency: int
  proxy: Optional[str]
  keymanager: KeyManager
  source_configs: Dict[str, Dict[str, Any]]
  httplib: Optional[str]
  http_timeout: int

def load_file(
  file: str, *,
  use_keymanager: bool,
) -> Tuple[Entries, Options]:
  try:
    with open(file, 'rb') as f:
      config = tomllib.load(f)
  except (OSError, tomllib.TOMLDecodeError) as e:
    raise FileLoadError('version configuration file', file, e)

  ver_files: Optional[Tuple[Path, Path]] = None
  keymanager = KeyManager(None)
  source_configs = {}

  if '__config__' in config:
    c = config.pop('__config__')
    d = Path(file).parent

    if 'oldver' in c and 'newver' in c:
      oldver_s = os.path.expandvars(
        os.path.expanduser(c.get('oldver')))
      oldver = d / oldver_s
      newver_s = os.path.expandvars(
        os.path.expanduser(c.get('newver')))
      newver = d / newver_s
      ver_files = oldver, newver

    if use_keymanager:
      keyfile = c.get('keyfile')
      if keyfile:
        keyfile_s = os.path.expandvars(
          os.path.expanduser(c.get('keyfile')))
        keyfile = d / keyfile_s
      keymanager = KeyManager(keyfile)

    if 'source' in c:
      source_configs = c['source']

    max_concurrency = c.get('max_concurrency', 20)
    proxy = c.get('proxy')
    httplib = c.get('httplib', None)
    http_timeout = c.get('http_timeout', 20)
  else:
    max_concurrency = 20
    proxy = None
    httplib = None
    http_timeout = 20

  return cast(Entries, config), Options(
    ver_files, max_concurrency, proxy, keymanager,
    source_configs, httplib, http_timeout,
  )

def setup_httpclient(
  max_concurrency: int = 20,
  httplib: Optional[str] = None,
  http_timeout: int = 20,
) -> Dispatcher:
  httplib_ = httplib or httpclient.find_best_httplib()
  httpclient.setup(
    httplib_, max_concurrency, http_timeout)
  return Dispatcher()

class Dispatcher:
  def dispatch(
    self,
    entries: Entries,
    task_sem: asyncio.Semaphore,
    result_q: Queue[RawResult],
    keymanager: KeyManager,
    entry_waiter: EntryWaiter,
    tries: int,
    source_configs: Dict[str, Dict[str, Any]],
  ) -> List[asyncio.Future]:
    mods: Dict[str, Tuple[types.ModuleType, List]] = {}
    ctx_tries.set(tries)
    ctx_entry_waiter.set(entry_waiter)
    root_ctx = contextvars.copy_context()

    for name, entry in entries.items():
      source = entry.get('source', 'none')
      if source not in mods:
        mod = import_module('nvchecker_source.' + source)
        tasks: List[Tuple[str, Entry]] = []
        mods[source] = mod, tasks
        config = source_configs.get(source)
        if config and getattr(mod, 'configure'):
          mod.configure(config)
      else:
        tasks = mods[source][1]
      tasks.append((name, entry))

    ret = []
    for mod, tasks in mods.values():
      if hasattr(mod, 'Worker'):
        worker_cls = mod.Worker
      else:
        worker_cls = FunctionWorker

      ctx = root_ctx.copy()
      worker = ctx.run(
        worker_cls,
        task_sem, result_q, tasks, keymanager,
      )
      if worker_cls is FunctionWorker:
        func = mod.get_version
        ctx.run(worker.initialize, func)

      ret.append(ctx.run(worker._run_maynot_raise))

    return ret

def substitute_version(
  version: str, conf: Entry,
) -> str:
  '''
  Substitute the version string via defined rules in the configuration file.
  See usage.rst#global-options for details.
  '''
  prefix = conf.get('prefix')
  if prefix:
    if version.startswith(prefix):
      version = version[len(prefix):]

  from_pattern = conf.get('from_pattern')
  if from_pattern:
    to_pattern = conf.get('to_pattern')
    if to_pattern is None:
      raise ValueError("from_pattern exists but to_pattern doesn't")

    version = re.sub(from_pattern, to_pattern, version)

  return version

def apply_list_options(
  versions: List[Union[str, RichResult]],
  conf: Entry,
  name: str,
) -> Optional[Union[str, RichResult]]:
  pattern = conf.get('include_regex')
  if versions and pattern:
    re_pat = re.compile(pattern)
    versions2 = [x for x in versions
                if re_pat.fullmatch(str(x))]
    if not versions2:
      logger.warning('include_regex matched no versions',
                     name=name, versions=versions, regex=pattern)
      return None
    versions = versions2

  pattern = conf.get('exclude_regex')
  if pattern:
    re_pat = re.compile(pattern)
    versions = [x for x in versions
                if not re_pat.fullmatch(str(x))]

  ignored = set(conf.get('ignored', '').split())
  if ignored:
    versions = [x for x in versions
                if str(x) not in ignored]

  if not versions:
    return None

  sort_version_key = sort_version_keys[
    conf.get("sort_version_key", "parse_version")]
  versions.sort(key=lambda version: sort_version_key(str(version))) # type: ignore

  return versions[-1]

def _process_result(r: RawResult) -> Union[RichResult, Exception]:
  version = r.version
  conf = r.conf
  name = r.name

  url = None
  revision = None
  gitref = None
  if isinstance(version, GetVersionError):
    kw = version.kwargs
    kw['name'] = name
    logger.error(version.msg, **kw)
    return version
  elif isinstance(version, Exception):
    logger.error('unexpected error happened',
                  name=r.name, exc_info=r.version)
    return version
  elif isinstance(version, list):
    version_str = apply_list_options(version, conf, name)
    if isinstance(version_str, RichResult):
      url = version_str.url
      gitref = version_str.gitref
      revision = version_str.revision
      version_str = version_str.version
  elif isinstance(version, RichResult):
    version_str = version.version
    url = version.url
    gitref = version.gitref
    revision = version.revision
  else:
    version_str = version

  if version_str:
    version_str = version_str.replace('\n', ' ')

    try:
      version_str = substitute_version(version_str, conf)
      return RichResult(
        version = version_str,
        url = url,
        gitref = gitref,
        revision = revision,
      )
    except (ValueError, re.error) as e:
      logger.exception('error occurred in version substitutions', name=name)
      return e

  else:
    return ValueError('no version returned')

def check_version_update(
  oldvers: ResultData,
  name: str,
  r: RichResult,
  verbose: bool,
) -> None:
  if old_result := oldvers.get(name):
    oldver = old_result.version
  else:
    oldver = None
  if not oldver or oldver != r.version:
    logger.info(
      'updated',
      name = name,
      version = r.version,
      revision = r.revision,
      old_version = oldver,
      url = r.url,
    )
  else:
    # provide visible user feedback if it was the only entry
    level = logging.INFO if verbose else logging.DEBUG
    logger.log(level, 'up-to-date', name=name, version=r.version, url=r.url)

async def process_result(
  oldvers: ResultData,
  result_q: Queue[RawResult],
  entry_waiter: EntryWaiter,
  verbose: bool = False,
) -> Tuple[ResultData, bool]:
  ret = {}
  has_failures = False
  try:
    while True:
      r = await result_q.get()
      try:
        r1 = _process_result(r)
      except Exception as e:
        logger.exception('error processing result', result=r)
        r1 = e
      if isinstance(r1, Exception):
        entry_waiter.set_exception(r.name, r1)
        # no versions are returned from "apply_list_options"?
        logger.error('no-result', name=r.name, error=repr(r1))
        has_failures = True
        continue
      check_version_update(oldvers, r.name, r1, verbose)
      entry_waiter.set_result(r.name, r1.version)
      ret[r.name] = r1
  except asyncio.CancelledError:
    return ret, has_failures

async def run_tasks(
  futures: Sequence[Awaitable[None]]
) -> None:
  for fu in asyncio.as_completed(futures):
    await fu
