# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_regex(get_version):
    assert await get_version("example", {
        "url": "https://httpbin.org/get",
        "regex": '"User-Agent": "(\w+)"',
        "user_agent": "Meow",
    }) == "Meow"
