# MIT licensed
# Copyright (c) 2021 ypsilik <tt2laurent.maud@gmail.com>, et al.

import pytest

pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

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
