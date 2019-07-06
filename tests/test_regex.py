# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_regex_httpbin_default_user_agent(get_version, httpbin):
    assert await get_version("example", {
        "url": httpbin.url + "/get",
        "regex": r'"User-Agent":\s*"([^"]+)"',
    }) == "lilydjwg/nvchecker"

async def test_regex_httpbin(get_version, httpbin):
    assert await get_version("example", {
        "url": httpbin.url + "/get",
        "regex": r'"User-Agent":\s*"([^"]+)"',
        "user_agent": "Meow",
    }) == "Meow"

async def test_regex(get_version):
    assert await get_version("example", {
        "url": "http://example.net/",
        "regex": r'for (\w+) examples',
    }) == "illustrative"

async def test_missing_ok(get_version):
    assert await get_version("example", {
        "url": "http://example.net/",
        "regex": "foobar",
        "missing_ok": True,
    }) is None
