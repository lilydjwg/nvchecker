# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Chih-Hsuan Yen <yan12125 at gmail dot com>

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@pytest.mark.flaky(reruns=10)
async def test_android_addon(get_version):
    assert await get_version("android-google-play-apk-expansion", {
        "source": "android_sdk",
        "android_sdk": "extras;google;market_apk_expansion",
        "repo": "addon",
    }) == "1.r03"

async def test_android_package(get_version):
    version = await get_version("android-sdk-cmake", {
        "source": "android_sdk",
        "android_sdk": "cmake;",
        "repo": "package",
    })
    assert version.startswith("4.")


async def test_android_package_channel(get_version):
    assert await get_version("android-sdk-cmake", {
        "source": "android_sdk",
        "android_sdk": "ndk;",
        "repo": "package",
        "channel": "beta,dev,canary",
    }) == "26.0.10636728"

async def test_android_list(get_version):
    assert await get_version("android-sdk-cmake-older", {
        "source": "android_sdk",
        "android_sdk": "cmake;",
        "repo": "package",
        "include_regex": r"3\.10.*",
    }) == "3.10.2"

async def test_android_package_os(get_version):
    assert await get_version("android-usb-driver", {
        "source": "android_sdk",
        "android_sdk": "extras;google;usb_driver",
        "repo": "addon",
        "host_os": "windows"
    }) == "13"

async def test_android_package_os_missing(get_version):
    assert await get_version("android-usb-driver", {
        "source": "android_sdk",
        "android_sdk": "extras;google;usb_driver",
        "repo": "addon",
        "host_os": "linux"
    }) == None
