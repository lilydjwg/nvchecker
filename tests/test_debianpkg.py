# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@pytest.mark.flaky(reruns=10)
async def test_debianpkg(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "debianpkg",
    }) == "0.1.7-3"

@pytest.mark.flaky(reruns=10)
async def test_debianpkg_strip_release(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "debianpkg",
        "strip_release": 1,
    }) == "0.1.7"

@pytest.mark.flaky(reruns=10)
async def test_debianpkg_suite(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "debianpkg",
        "suite": "buster",
    }) == "0.1.6-1"
