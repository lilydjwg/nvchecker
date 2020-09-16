# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

from flaky import flaky
import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@flaky(max_runs=10)
async def test_apt(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "apt",
    }) == "0.1.7-1"

@flaky(max_runs=10)
async def test_apt_source_pkg(get_version):
    assert await get_version("test", {
        "source": "apt",
        "source_pkg": "golang-github-dataence-porter2",
    }) == "0.0~git20150829.56e4718-2"

@flaky(max_runs=10)
async def test_apt_strip_release(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "apt",
        "strip_release": 1,
    }) == "0.1.7"

@flaky(max_runs=10)
async def test_apt_deepin(get_version):
    assert await get_version("sigrok-firmware-fx2lafw", {
        "source": "apt",
        "mirror": "https://community-packages.deepin.com/deepin",
        "suite": "apricot",
    }) == "0.1.6-1"
