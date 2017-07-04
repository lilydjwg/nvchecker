import configparser
import pytest
import asyncio

from nvchecker.get_version import get_version as _get_version

@pytest.fixture(scope="module")
async def get_version():
    async def __call__(name, config):

        if isinstance(config, dict):
            _config = configparser.ConfigParser(dict_type=dict, allow_no_value=True)
            _config.read_dict({name: config})
            config = _config[name]

        return (await _get_version(name, config))[1]

    return __call__

@pytest.yield_fixture(scope="module")
def event_loop(request):
    """Override pytest-asyncio's event_loop fixture,
       Don't create an instance of the default event loop for each test case.
    """
    loop = asyncio.get_event_loop()
    yield loop
