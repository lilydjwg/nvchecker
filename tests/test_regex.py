# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import base64

import pytest
import pytest_httpbin
assert pytest_httpbin  # for pyflakes

pytestmark = pytest.mark.asyncio

def base64_encode(s):
    return base64.b64encode(s.encode('utf-8')).decode('ascii')

async def test_regex_httpbin_default_user_agent(get_version, httpbin):
    ua = await get_version("example", {
        "source": "regex",
        "url": httpbin.url + "/get",
        "regex": r'"User-Agent":\s*"([^"]+)"',
    })
    assert ua.startswith("lilydjwg/nvchecker")

async def test_regex_httpbin_user_agent(get_version, httpbin):
    assert await get_version("example", {
        "source": "regex",
        "url": httpbin.url + "/get",
        "regex": r'"User-Agent":\s*"(\w+)"',
        "user_agent": "Meow",
    }) == "Meow"

async def test_regex(get_version, httpbin):
    assert await get_version("example", {
        "source": "regex",
        "url": httpbin.url + "/base64/" + base64_encode("version 1.12 released"),
        "regex": r'version ([0-9.]+)',
    }) == "1.12"

async def test_missing_ok(get_version, httpbin):
    assert await get_version("example", {
        "source": "regex",
        "url": httpbin.url + "/base64/" + base64_encode("something not there"),
        "regex": "foobar",
        "missing_ok": True,
    }) is None

async def test_regex_with_tokenBasic(get_version, httpbin):
    assert await get_version("example", {
        "source": "regex",
        "url": httpbin.url + "/basic-auth/username/superpassword",
        "httptoken_example": "Basic dXNlcm5hbWU6c3VwZXJwYXNzd29yZA==",
        "regex": r'"user":"([a-w]+)"',
    }) == "username"

async def test_regex_with_tokenBearer(get_version, httpbin):
    assert await get_version("example", {
        "source": "regex",
        "url": httpbin.url + "/bearer",
        "httptoken_example": "Bearer username:password",
        "regex": r'"token":"([a-w]+):.*"',
    }) == "username"