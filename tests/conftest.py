# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

import asyncio
import structlog
from typing import Optional

import toml
import pytest

from nvchecker import core
from nvchecker import __main__ as main
from nvchecker.util import Entries, VersData, RawResult

async def run(
  entries: Entries, max_concurrency: int = 20,
  keys_toml: Optional[str] = None,
) -> VersData:
  token_q = core.token_queue(max_concurrency)
  result_q: asyncio.Queue[RawResult] = asyncio.Queue()
  if keys_toml:
    keymanager = core.KeyManager.from_str(keys_toml)
  else:
    keymanager = core.KeyManager(None)

  futures = core.dispatch(
    entries, token_q, result_q,
    keymanager, 1,
  )

  oldvers: VersData = {}
  result_coro = core.process_result(oldvers, result_q)
  runner_coro = core.run_tasks(futures)

  return await main.run(result_coro, runner_coro)

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
    entries = toml.loads(str)
    newvers = await run(entries)
    return newvers.popitem()[1]

  return __call__

@pytest.fixture(scope="module")
async def run_str_multi():
  async def __call__(str):
    entries = toml.loads(str)
    newvers = await run(entries)
    return newvers

  return __call__

@pytest.fixture(scope="session")
def event_loop(request):
  """Override pytest-asyncio's event_loop fixture,
     Don't create an instance of the default event loop for each test case.
     We need the same ioloop across tests for the aiohttp support.
  """
  loop = asyncio.get_event_loop()
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
