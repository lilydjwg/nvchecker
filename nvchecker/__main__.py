#!/usr/bin/env python3
# MIT licensed
# Copyright (c) 2013-2024 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import sys
import argparse
import asyncio
from typing import Coroutine, Tuple
from pathlib import Path

import structlog

from . import core
from .util import ResultData, RawResult, KeyManager, EntryWaiter
from .ctxvars import proxy as ctx_proxy

logger = structlog.get_logger(logger_name=__name__)

def main() -> None:
  parser = argparse.ArgumentParser(description='New version checker for software')
  parser.add_argument('-k', '--keyfile',
                      metavar='FILE', type=str,
                      help='use specified keyfile (override the one in configuration file)')
  parser.add_argument('-t', '--tries', default=1, type=int, metavar='N',
                      help='try N times when network errors occur')
  parser.add_argument('--failures', action='store_true',
                      help='exit with code 3 if failures / errors happen during checking')
  parser.add_argument('-e', '--entry', type=str,
                      help='only execute on specified entry (useful for debugging)')
  core.add_common_arguments(parser)
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  try:
    entries, options = core.load_file(
      args.file, use_keymanager=not bool(args.keyfile))

    if args.entry:
      if args.entry not in entries:
        sys.exit('Specified entry not found in config')
      entries = {args.entry: entries[args.entry]}

    if args.keyfile:
      keymanager = KeyManager(Path(args.keyfile))
    else:
      keymanager = options.keymanager
  except core.FileLoadError as e:
    sys.exit(str(e))

  if options.proxy is not None:
    ctx_proxy.set(options.proxy)

  task_sem = asyncio.Semaphore(options.max_concurrency)
  result_q: asyncio.Queue[RawResult] = asyncio.Queue()
  dispatcher = core.setup_httpclient(
    options.max_concurrency,
    options.httplib,
    options.http_timeout,
  )
  entry_waiter = EntryWaiter()
  try:
    futures = dispatcher.dispatch(
      entries, task_sem, result_q,
      keymanager, entry_waiter,
      args.tries,
      options.source_configs,
    )
  except ModuleNotFoundError as e:
    sys.exit(f'Error: {e}')

  if options.ver_files is not None:
    oldvers = core.read_verfile(options.ver_files[0])
  else:
    oldvers = {}
  result_coro = core.process_result(oldvers, result_q, entry_waiter, verbose=bool(args.entry))
  runner_coro = core.run_tasks(futures)

  if sys.version_info >= (3, 10):
    # Python 3.10 has deprecated asyncio.get_event_loop
    results, has_failures = asyncio.run(run(result_coro, runner_coro))
  else:
    # Python < 3.10 will create an eventloop when asyncio.Queue is initialized
    results, has_failures = asyncio.get_event_loop().run_until_complete(run(result_coro, runner_coro))

  if options.ver_files is not None:
    newverf = options.ver_files[1]
    if args.entry:
      # don't remove other entries when only one entry is specified on cmdline
      vers = core.read_verfile(newverf)
    else:
      vers = {}
    vers.update(results)
    core.write_verfile(newverf, vers)

  if args.failures and has_failures:
    sys.exit(3)

async def run(
  result_coro: Coroutine[None, None, Tuple[ResultData, bool]],
  runner_coro: Coroutine[None, None, None],
) -> Tuple[ResultData, bool]:
  result_fu = asyncio.create_task(result_coro)
  runner_fu = asyncio.create_task(runner_coro)
  await runner_fu
  result_fu.cancel()
  return await result_fu

if __name__ == '__main__':
  main()
