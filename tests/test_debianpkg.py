# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

from flaky import flaky
import pytest
pytestmark = pytest.mark.asyncio

@flaky(max_runs=10)
async def test_debianpkg(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {"debianpkg": None}) == "0.1.6-1"

@flaky(max_runs=10)
async def test_debianpkg_strip_release(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {"debianpkg": None, "strip-release": 1}) == "0.1.6"

@flaky(max_runs=10)
async def test_debianpkg_suite(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {"debianpkg": None, "suite": "jessie"}) == "0.1.2-1"

@flaky(max_runs=10)
async def test_debianpkg_numbered(get_version):
    assert await get_version("sigrok-firmware-fx2lafw:1", {"debianpkg": None}, clear_cache=True) == "0.1.6-1"
