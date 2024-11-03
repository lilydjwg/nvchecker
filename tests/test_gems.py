# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_gems(get_version):
    assert await get_version("example", {
        "source": "gems",
    }) == "1.0.2"
