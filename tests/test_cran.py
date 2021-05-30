# MIT licensed
# Copyright (c) 2021- hubutui <hot123tea123@gmail.com>

import pytest

pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_cran(get_version):
    assert await get_version("ggplot2", {
        "source": "cran",
    }) == "3.3.3"
