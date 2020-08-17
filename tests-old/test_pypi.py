# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_pypi(get_version):
    assert await get_version("example", {"pypi": None}) == "0.1.0"

async def test_pypi_release(get_version):
    assert await get_version("example-test-package", {"pypi": "example-test-package"}) == "1.0.0"

async def test_pypi_pre_release(get_version):
    assert await get_version("example-test-package", {"pypi": "example-test-package", "use_pre_release": 1}) == "1.0.1a1"
