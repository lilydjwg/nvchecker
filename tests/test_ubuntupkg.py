# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

from flaky import flaky
import pytest
pytestmark = pytest.mark.asyncio

@flaky
async def test_ubuntupkg(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {"ubuntupkg": None}) == "0.1.6-1"

@flaky
async def test_ubuntupkg_strip_release(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {"ubuntupkg": None, "strip-release": 1}) == "0.1.6"

@flaky
async def test_ubuntupkg_suite(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {"ubuntupkg": None, "suite": "xenial"}) == "0.1.2-1"

@flaky
async def test_ubuntupkg_suite_with_paging(get_version):
    assert await get_version("ffmpeg", {"ubuntupkg": None, "suite": "xenial"}) == "7:2.8.15-0ubuntu0.16.04.1"

@flaky
async def test_ubuntupkg_numbered(get_version):
    assert await get_version("sigrok-firmware-fx2lafw:1", {"ubuntupkg": None}, clear_cache=True) == "0.1.6-1"
