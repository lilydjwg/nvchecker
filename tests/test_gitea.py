# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.needs_net]

async def test_gitea(get_version):
    ver = await get_version("example",
                            {"gitea": "gitea/tea"})
    assert len(ver) == 8
    assert ver.isdigit()

async def test_gitea_max_tag(get_version):
    assert await get_version("example", {"gitea": "gitea/tea", "use_max_tag": 1}) == "v0.4.0"

async def test_gitea_max_tag_with_ignored_tags(get_version):
    assert await get_version("example", {"gitea": "gitea/tea", "use_max_tag": 1, "ignored_tags": "v0.4.0"}) == "v0.3.1"

async def test_gitea_max_tag_with_include(get_version):
    assert await get_version("example", {
        "gitea": "gitea/tea", "use_max_tag": 1,
        "include_regex": r'v0\.3.*',
    }) == "v0.3.1"
