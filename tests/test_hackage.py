# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from flaky import flaky
import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@flaky(max_runs=10)
async def test_hackage(get_version):
    assert await get_version("sessions", {
        "source": "hackage",
    }) == "2008.7.18"
