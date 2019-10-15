# MIT licensed
# Copyright (c) 2017 Yen Chi Hsuan <yan12125 at gmail dot com>

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_android_addon(get_version):
    assert await get_version("android-google-play-apk-expansion", {"android_sdk": "extras;google;market_apk_expansion", "repo": "addon"}) == "1.r03"

async def test_android_package(get_version):
    assert await get_version("android-sdk-cmake", {"android_sdk": "cmake;", "repo": "package"}) == "3.6.4111459"
