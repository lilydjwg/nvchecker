# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_pypi(get_version):
    assert await get_version("example", {
        "source": "pypi",
    }) == "0.1.0"

async def test_pypi_release(get_version):
    assert await get_version("example-test-package", {
        "source": "pypi",
        "pypi": "example-test-package",
    }) == "1.0.0"

async def test_pypi_pre_release(get_version):
    assert await get_version("example-test-package", {
        "source": "pypi",
        "use_pre_release": 1,
    }) == "1.0.1a1"

async def test_pypi_list(get_version):
    assert await get_version("urllib3", {
        "source": "pypi",
        "include_regex": "^1\\..*",
    }) == "1.26.20"

async def test_pypi_invalid_version(get_version):
    await get_version("sympy", {
        "source": "pypi",
    })

async def test_pypi_yanked_version(get_version):
    assert await get_version("urllib3", {
        "source": "pypi",
        "include_regex": "^(1\\..*)|(2\\.0\\.[0,1])",
    }) == "1.26.20"
