# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.needs_net]

@pytest.mark.flaky(reruns=10)
async def test_gitea(get_version):
    ver = await get_version("example", {
        "source": "gitea",
        "gitea": "gitea/tea"})
    assert ver.startswith('20')
    assert 'T' in ver

@pytest.mark.flaky(reruns=10)
async def test_gitea_max_tag_with_include(get_version):
    assert await get_version("example", {
        "source": "gitea",
        "gitea": "gitea/tea",
        "use_max_tag": True,
        "include_regex": r'v0\.3.*',
    }) == "v0.3.1"

async def test_gitea_latest_release(get_version):
    ver = await get_version("example", {
        "source": "gitea",
        "host": "codeberg.org",
        "gitea": "ciberandy/qiv",
        "use_latest_release": True,
    })
    assert ver.startswith('v3.'), ver

