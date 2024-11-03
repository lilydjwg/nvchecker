# MIT licensed
# Copyright (c) 2020-2021 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@pytest.mark.flaky(reruns=10)
async def test_apt(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "apt",
        "mirror": "http://deb.debian.org/debian/",
        "suite": "sid",
    }) == "0.1.7-3"

@pytest.mark.flaky(reruns=10)
async def test_apt_srcpkg(get_version):
    ver = await get_version("test", {
        "source": "apt",
        "srcpkg": "golang-github-dataence-porter2",
        "mirror": "http://deb.debian.org/debian/",
        "suite": "sid",
    })
    assert ver.startswith("0.0~git20150829.56e4718-")

@pytest.mark.flaky(reruns=10)
async def test_apt_strip_release(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "apt",
        "mirror": "http://deb.debian.org/debian/",
        "suite": "sid",
        "strip_release": 1,
    }) == "0.1.7"

@pytest.mark.skip
@pytest.mark.flaky(reruns=10)
async def test_apt_deepin(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "apt",
        "mirror": "https://community-packages.deepin.com/deepin",
        "suite": "apricot",
    }) == "0.1.6-1"

