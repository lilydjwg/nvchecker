# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_gems(get_version):
    assert await get_version("example", {"gems": None}) == "1.0.2"

async def test_gems_numbered(get_version):
    assert await get_version("example:1", {"gems": None}, clear_cache=True) == "1.0.2"
