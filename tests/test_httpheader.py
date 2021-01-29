# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest

pytestmark = pytest.mark.asyncio

async def test_redirection(get_version):
    assert await get_version("unifiedremote", {
        "source": "httpheader",
        "url": "https://www.unifiedremote.com/download/linux-x64-deb",
        "regex": r'urserver-([\d.]+).deb',
    }) != None

