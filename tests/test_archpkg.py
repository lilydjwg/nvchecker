# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from flaky import flaky
import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@flaky
async def test_archpkg(get_version):
    assert await get_version("ipw2100-fw", {
        "source": "archpkg",
    }) == "1.3-10"

@flaky
async def test_archpkg_strip_release(get_version):
    assert await get_version("ipw2100-fw", {
        "source": "archpkg",
        "strip_release": True,
    }) == "1.3"

@flaky
async def test_archpkg_provided(get_version):
    assert await get_version("dbus", {
        "source": "archpkg",
        "provided": "libdbus-1.so",
    }) == "3-64"

@flaky
async def test_archpkg_provided_strip(get_version):
    assert await get_version("jsoncpp", {
        "source": "archpkg",
        "provided": "libjsoncpp.so",
        "strip_release": True,
    }) == "24"

