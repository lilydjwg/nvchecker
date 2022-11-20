# MIT licensed
# Copyright (c) 2021 ypsilik <tt2laurent.maud@gmail.com>, et al.

import pytest

lxml_available = True
try:
  import lxml
except ImportError:
  lxml_available = False

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.needs_net,
  pytest.mark.skipif(not lxml_available, reason="needs lxml"),
]

async def test_xpath_ok(get_version):
    assert await get_version("unifiedremote", {
        "source": "htmlparser",
        "url": "http://httpbin.org/",
        "xpath": '//pre[@class="version"]/text()',
    }) != None

async def test_xpath_missing_ok(get_version):
    assert await get_version("unifiedremote", {
        "source": "htmlparser",
        "url": "http://httpbin.org/",
        "xpath": '//pre[@class="test-is-ok"]/text()',
        "missing_ok": True,
    }) is None

async def test_xpath_element(get_version):
    assert await get_version("unifiedremote", {
        "source": "htmlparser",
        "url": "http://httpbin.org/",
        "xpath": '//pre[@class="version"]',
    }) != None

