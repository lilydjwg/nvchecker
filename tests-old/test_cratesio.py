# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_cratesio(get_version):
    assert await get_version("example", {"cratesio": None}) == "0.1.0"
