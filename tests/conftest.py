import configparser
import pytest
import asyncio
import io

from nvchecker.get_version import get_version as _get_version
from nvchecker.core import Source

class TestSource(Source):
    def __init__(self, future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._future = future

    def on_update(self, name, version, oldver):
        self._future.set_result(version)

    def on_exception(self, name, exc):
        self._future.set_exception(exc)

@pytest.fixture(scope="module")
async def run_source():
    async def __call__(conf):
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
            _config = configparser.ConfigParser(dict_type=dict, allow_no_value=True)
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
