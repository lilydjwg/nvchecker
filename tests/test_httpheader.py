# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest

pytestmark = pytest.mark.asyncio

async def test_redirection(get_version):
    assert await get_version("jmeter-plugins-manager", {
        "source": "httpheader",
        "url": "https://jmeter-plugins.org/get/",
        "regex": r'/([\d.]+)/',
    }) == "1.6"

