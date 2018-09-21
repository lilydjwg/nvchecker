# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

@pytest.mark.skipif(True,
                    reason='httpbin is overloaded?')
async def test_regex_httpbin(get_version):
    assert await get_version("example", {
        "url": "https://httpbin.org/get",
        "regex": '"User-Agent": "(\w+)"',
        "user_agent": "Meow",
    }) == "Meow"

async def test_regex(get_version):
    assert await get_version("example", {
        "url": "https://example.net/",
        "regex": 'for (\w+) examples',
    }) == "illustrative"

async def test_missing_ok(get_version, raise_on_logger_msg):
    assert await get_version("example", {
        "url": "https://example.net/",
        "regex": "foobar",
        "missing_ok": True,
    }) is None
