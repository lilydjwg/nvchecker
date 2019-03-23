# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_npm(get_version):
    assert await get_version("example", {"npm": None}) == "0.0.0"

async def test_npm_numbered(get_version):
    assert await get_version("example:1", {"npm": None}, clear_cache=True) == "0.0.0"
