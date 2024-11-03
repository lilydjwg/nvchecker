# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@pytest.mark.flaky
async def test_archpkg(get_version):
    assert await get_version("base", {
        "source": "archpkg",
    }) == "3-2"

@pytest.mark.flaky
async def test_archpkg_strip_release(get_version):
    assert await get_version("base", {
        "source": "archpkg",
        "strip_release": True,
    }) == "3"

@pytest.mark.flaky
async def test_archpkg_provided(get_version):
    assert await get_version("dbus", {
        "source": "archpkg",
        "provided": "libdbus-1.so",
    }) == "3-64"

@pytest.mark.flaky
async def test_archpkg_provided_strip(get_version):
    int(await get_version("jsoncpp", {
        "source": "archpkg",
        "provided": "libjsoncpp.so",
        "strip_release": True,
    }))

