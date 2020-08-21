#!/usr/bin/env python3
# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import sys
import argparse
import asyncio
from typing import Coroutine
from pathlib import Path

import structlog

from . import core
from .util import VersData, RawResult, KeyManager

logger = structlog.get_logger(logger_name=__name__)

def main() -> None:
  parser = argparse.ArgumentParser(description='New version checker for software')
  parser.add_argument('-k', '--keyfile',
                      metavar='FILE', type=str,
                      help='use specified keyfile')
  parser.add_argument('-t', '--tries', default=1, type=int, metavar='N',
                      help='try N times when network errors occur')
  core.add_common_arguments(parser)
  args = parser.parse_args()
  if core.process_common_arguments(args):
    return

  if not args.file:
    try:
      file = open(core.get_default_config())
    except FileNotFoundError:
      sys.exit('version configuration file not given and default does not exist')
  else:
    file = args.file

  entries, options = core.load_file(
    file, use_keymanager=bool(args.keyfile))

  if args.keyfile:
    keymanager = KeyManager(Path(args.keyfile))
  else:
    keymanager = options.keymanager

  token_q = core.token_queue(options.max_concurrency)
  result_q: asyncio.Queue[RawResult] = asyncio.Queue()
  try:
    futures = core.dispatch(
      entries, token_q, result_q,
      keymanager, args.tries,
    )
  except ModuleNotFoundError as e:
    sys.exit(f'Error: {e}')

  if options.ver_files is not None:
    oldvers = core.read_verfile(options.ver_files[0])
  else:
    oldvers = {}
  result_coro = core.process_result(oldvers, result_q)
  runner_coro = core.run_tasks(futures)

  # asyncio.run doesn't work because it always creates new eventloops
  loop = asyncio.get_event_loop()
  newvers = loop.run_until_complete(run(result_coro, runner_coro))

  if options.ver_files is not None:
    core.write_verfile(options.ver_files[1], newvers)

async def run(
  result_coro: Coroutine[None, None, VersData],
  runner_coro: Coroutine[None, None, None],
) -> VersData:
  result_fu = asyncio.create_task(result_coro)
  runner_fu = asyncio.create_task(runner_coro)
  await runner_fu
  result_fu.cancel()
  return await result_fu

if __name__ == '__main__':
  main()
