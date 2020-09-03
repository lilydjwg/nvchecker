# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

from flaky import flaky
import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@flaky(max_runs=10)
async def test_debianpkg(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "debianpkg",
    }) == "0.1.7-1"

@flaky(max_runs=10)
async def test_debianpkg_strip_release(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "debianpkg",
        "strip_release": 1,
    }) == "0.1.7"

@flaky(max_runs=10)
async def test_debianpkg_suite(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "debianpkg",
        "suite": "buster",
    }) == "0.1.6-1"
