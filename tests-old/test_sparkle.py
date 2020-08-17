# MIT licensed
# Copyright (c) 2020 Sunlei <guizaicn@gmail.com>

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_sparkle(get_version):
    assert await get_version("example", {"sparkle": "https://sparkle-project.org/files/sparkletestcast.xml"}) == "2.0"
