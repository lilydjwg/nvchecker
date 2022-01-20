# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio
import structlog
import os
from pathlib import Path

import tomli
import pytest

from nvchecker import core
from nvchecker import __main__ as main
from nvchecker.util import Entries, VersData, RawResult

use_keyfile = False

async def run(
  entries: Entries, max_concurrency: int = 20,
) -> VersData:
  task_sem = asyncio.Semaphore(max_concurrency)
  result_q: asyncio.Queue[RawResult] = asyncio.Queue()
  keyfile = os.environ.get('KEYFILE')
  if use_keyfile and keyfile:
    filepath = Path(keyfile)
    keymanager = core.KeyManager(filepath)
  else:
    keymanager = core.KeyManager(None)

  dispatcher = core.setup_httpclient()
  entry_waiter = core.EntryWaiter()
  futures = dispatcher.dispatch(
    entries, task_sem, result_q,
    keymanager, entry_waiter, 1, {},
  )

  oldvers: VersData = {}
  result_coro = core.process_result(oldvers, result_q, entry_waiter)
  runner_coro = core.run_tasks(futures)

  vers, _has_failures = await main.run(result_coro, runner_coro)
  return vers

@pytest.fixture(scope="module")
async def get_version():
  async def __call__(name, config):
    entries = {name: config}
    newvers = await run(entries)
    return newvers.get(name)

  return __call__

@pytest.fixture(scope="module")
async def run_str():
  async def __call__(str):
    entries = tomli.loads(str)
    newvers = await run(entries)
    return newvers.popitem()[1]

  return __call__

@pytest.fixture(scope="module")
async def run_str_multi():
  async def __call__(str):
    entries = tomli.loads(str)
    newvers = await run(entries)
    return newvers

  return __call__

loop = asyncio.new_event_loop()
@pytest.fixture(scope="session")
def event_loop(request):
  """Override pytest-asyncio's event_loop fixture,
     Don't create an instance of the default event loop for each test case.
     We need the same ioloop across tests for the aiohttp support.
  """
  yield loop

@pytest.fixture(scope="session", autouse=True)
def raise_on_logger_msg():
  def proc(logger, method_name, event_dict):
    if method_name in ('warning', 'error'):
      if 'exc_info' in event_dict:
        raise event_dict['exc_info']
      if not event_dict['event'].startswith(('rate limited', 'no-result')):
        raise RuntimeError(event_dict['event'])
    return event_dict['event']

  structlog.configure([proc])

def pytest_configure(config):
  # register an additional marker
  config.addinivalue_line(
    'markers', 'needs_net: mark test to require Internet access',
  )

@pytest.fixture
def keyfile():
  global use_keyfile
  if 'KEYFILE' not in os.environ:
    pytest.skip('KEYFILE not set')
    return

  use_keyfile = True
  yield
  use_keyfile = False
