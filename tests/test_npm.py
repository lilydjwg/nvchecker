# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_npm(get_version):
    assert await get_version("example", {
        "source": "npm",
    }) == "0.0.0"
