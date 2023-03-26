# MIT licensed
# Copyright (c) 2013-2021 Th3Whit3Wolf <the.white.wolf.is.1337@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_vsmarketplace(get_version):
    assert await get_version("usernamehw.indent-one-space", {
        "source": "vsmarketplace",
    }) == "1.0.0"
