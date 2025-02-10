# MIT licensed
# Copyright (c) 2020,2024 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@pytest.mark.flaky
async def test_ubuntupkg(get_version):
    v = await get_version("sigrok-firmware-fx2lafw", {
        "source": "ubuntupkg",
    })
    assert v.startswith("0.1.7-")

@pytest.mark.flaky
async def test_ubuntupkg_strip_release(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "ubuntupkg",
        "strip_release": True,
    }) == "0.1.7"

@pytest.mark.flaky
async def test_ubuntupkg_suite(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "ubuntupkg",
        "suite": "xenial",
    }) == "0.1.2-1"

@pytest.mark.flaky(reruns=10)
async def test_ubuntupkg_suite_with_paging(get_version):
    assert await get_version("ffmpeg", {
        "source": "ubuntupkg",
        "suite": "xenial",
    }) == "7:2.8.17-0ubuntu0.1"
