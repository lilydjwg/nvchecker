# MIT licensed
# Copyright (c) 2013-2021 Th3Whit3Wolf <the.white.wolf.is.1337@gmail.com>, et al.

import os
import pytest

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.needs_net,
    pytest.mark.skipif(bool(os.environ.get('GITHUB_RUN_ID')), reason="503 for GitHub Actions"),
]

async def test_openvsx(get_version):
    assert await get_version("usernamehw.indent-one-space", {
        "source": "openvsx",
    }) == "0.3.0"
