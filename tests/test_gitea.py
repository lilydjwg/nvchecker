# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio(scope="session"),
              pytest.mark.needs_net]

@pytest.mark.flaky(reruns=10)
async def test_gitea(get_version):
    ver = await get_version("example", {
        "source": "gitea",
        "gitea": "gitea/tea"})
    assert len(ver) == 8
    assert ver.isdigit()

@pytest.mark.flaky(reruns=10)
async def test_gitea_max_tag_with_include(get_version):
    assert await get_version("example", {
        "source": "gitea",
        "gitea": "gitea/tea",
        "use_max_tag": True,
        "include_regex": r'v0\.3.*',
    }) == "v0.3.1"
