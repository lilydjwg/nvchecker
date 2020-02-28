import configparser
import pytest
import asyncio
import io
import structlog

from nvchecker.get_version import get_version as _get_version
from nvchecker.get_version import _cache
from nvchecker.core import Source

class TestSource(Source):
  def __init__(self, future, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._future = future

  def on_update(self, name, version, oldver):
    self._future.set_result(version)

  def on_no_result(self, name):
    self._future.set_result(None)

  def on_exception(self, name, exc):
    self._future.set_exception(exc)

@pytest.fixture(scope="module")
async def run_source():
  async def __call__(conf, *, clear_cache=False):
    if clear_cache:
      _cache.clear()

    future = asyncio.Future()
    file = io.StringIO(conf)
    file.name = '<StringIO>'

    s = TestSource(future, file)
    await s.check()
    return await future

  return __call__

@pytest.fixture(scope="module")
async def get_version():
  async def __call__(name, config):

    if isinstance(config, dict):
      _config = configparser.ConfigParser(
        dict_type=dict, allow_no_value=True,
        interpolation=None,
      )
      _config.read_dict({name: config})
      config = _config[name]

    return await _get_version(name, config)

  return __call__

@pytest.fixture(scope="module")
def event_loop(request):
  """Override pytest-asyncio's event_loop fixture,
     Don't create an instance of the default event loop for each test case.
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
