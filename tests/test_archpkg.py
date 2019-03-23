# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from flaky import flaky
import pytest
pytestmark = pytest.mark.asyncio

@flaky
async def test_archpkg(get_version):
    assert await get_version("ipw2100-fw", {"archpkg": None}) == "1.3-9"

@flaky
async def test_archpkg_strip_release(get_version):
    assert await get_version("ipw2100-fw", {"archpkg": None, "strip-release": 1}) == "1.3"

@flaky
async def test_archpkg_numbered(get_version):
    assert await get_version("ipw2100-fw:1", {"archpkg": None}, clear_cache=True) == "1.3-9"
