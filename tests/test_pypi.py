# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_pypi(get_version):
    assert await get_version("example", {"pypi": None}) == "0.1.0"
