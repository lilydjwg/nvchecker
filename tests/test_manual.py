# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_manual(get_version):
    assert await get_version("example", {
        "source": "manual",
        "manual": "Meow",
    }) == "Meow"
