# MIT licensed
# Copyright (c) 2013-2020,2024 lilydjwg <lilydjwg@gmail.com>, et al.

import base64

import pytest

httpbin_available = True
try:
  import pytest_httpbin
  assert pytest_httpbin # for pyflakes
except ImportError:
  httpbin_available = False

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.skipif(not httpbin_available, reason="needs pytest_httpbin"),
]

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

async def test_missing(get_version, httpbin):
  with pytest.raises(RuntimeError):
    await get_version("example", {
      "source": "regex",
      "url": httpbin.url + "/base64/" + base64_encode("something not there"),
      "regex": "foobar",
    })

async def test_multi_group(get_version, httpbin):
  with pytest.raises(RuntimeError):
    await get_version("example", {
      "source": "regex",
      "url": httpbin.url + "/base64/" + base64_encode("1.2"),
      "regex": r"(\d+)\.(\d+)",
    })

async def test_regex_with_tokenBasic(get_version, httpbin):
  assert await get_version("example", {
    "source": "regex",
    "url": httpbin.url + "/basic-auth/username/superpassword",
    "httptoken": "Basic dXNlcm5hbWU6c3VwZXJwYXNzd29yZA==",
    "regex": r'"user":\s*"([a-w]+)"',
  }) == "username"

async def test_regex_with_tokenBearer(get_version, httpbin):
  assert await get_version("example", {
    "source": "regex",
    "url": httpbin.url + "/bearer",
    "httptoken": "Bearer username:password",
    "regex": r'"token":\s*"([a-w]+):.*"',
  }) == "username"

async def test_regex_no_verify_ssl(get_version, httpbin_secure):
  assert await get_version("example", {
    "source": "regex",
    "url": httpbin_secure.url + "/base64/" + base64_encode("version 1.12 released"),
    "regex": r'version ([0-9.]+)',
    "verify_cert": False,
  }) == "1.12"

async def test_regex_bad_ssl(get_version, httpbin_secure):
  try:
    await get_version("example", {
      "source": "regex",
      "url": httpbin_secure.url + "/base64/" + base64_encode("version 1.12 released"),
      "regex": r'version ([0-9.]+)',
    })
  except Exception:
    pass
  else:
    assert False, 'certificate should not be trusted'

async def test_regex_post(get_version, httpbin):
  assert await get_version("example", {
    "source": "regex",
    "url": httpbin.url + "/post",
    "regex": r'"ABCDEF":\s*"(\w+)"',
    "post_data": "ABCDEF=234&CDEFG=xyz"
  }) == "234"

async def test_regex_post2(get_version, httpbin):
  assert await get_version("example", {
    "source": "regex",
    "url": httpbin.url + "/post",
    "regex": r'"CDEFG":\s*"(\w+)"',
    "post_data": "ABCDEF=234&CDEFG=xyz"
  }) == "xyz"

async def test_regex_post_json(get_version, httpbin):
  assert await get_version("example", {
    "source": "regex",
    "url": httpbin.url + "/post",
    "regex": r'"ABCDEF":\s*(\w+)',
    "post_data": '{"ABCDEF":234,"CDEFG":"xyz"}',
    "post_data_type": "application/json"
  }) == "234"

async def test_regex_post_json2(get_version, httpbin):
  assert await get_version("example", {
    "source": "regex",
    "url": httpbin.url + "/post",
    "regex": r'"CDEFG":\s*"(\w+)"',
    "post_data": '{"ABCDEF":234,"CDEFG":"xyz"}',
    "post_data_type": "application/json"
  }) == "xyz"
