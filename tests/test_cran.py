# MIT licensed
# Copyright (c) 2022 Pekka Ristola <pekkarr [at] protonmail [dot] com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_cran(get_version):
    ver = await get_version("xml2", {
        "source": "cran",
    })
    assert ver.startswith("1.5.")
