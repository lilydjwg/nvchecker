# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_manual(get_version):
    assert await get_version("example", {"manual": "Meow"}) == "Meow"
