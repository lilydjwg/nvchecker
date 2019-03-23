# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_packagist(get_version):
    assert await get_version("butterfly/example-web-application", {"packagist": None}) == "1.2.0"

async def test_packagist_numbered(get_version):
    assert await get_version("butterfly/example-web-application:1", {"packagist": None}, clear_cache=True) == "1.2.0"
