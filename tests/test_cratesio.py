# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_cratesio(get_version):
    assert await get_version("example", {"cratesio": None}) == "0.1.0"

async def test_cratesio_numbered(get_version):
    assert await get_version("example:1", {"cratesio": None}, clear_cache=True) == "0.1.0"
