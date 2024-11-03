# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@pytest.mark.flaky(reruns=10)
async def test_hackage(get_version):
    assert await get_version("sessions", {
        "source": "hackage",
    }) == "2008.7.18"
