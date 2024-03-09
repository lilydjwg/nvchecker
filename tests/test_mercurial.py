# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_mercurial(get_version):
    assert await get_version("example", {
        "source": "mercurial",
        "mercurial": "https://www.mercurial-scm.org/repo/users/sid0/hg-git",
    }) == "0.8.0"
