# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_cpan(get_version):
    assert await get_version("POE-Component-Server-HTTPServer", {"cpan": None}) == "0.9.2"
