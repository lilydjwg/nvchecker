# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2020 Sunlei <guizaicn@gmail.com>

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_sparkle(get_version):
    assert await get_version("example", {
        "source": "sparkle",
        "sparkle": "https://raw.githubusercontent.com/sparkle-project/Sparkle/master/Tests/Resources/testlocalizedreleasenotesappcast.xml",
    }) == "6.0"
