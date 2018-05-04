# MIT licensed
# Copyright (c) 2013-2018 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import re
import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.skipif("NVCHECKER_GITHUB_TOKEN" not in os.environ,
                                 reason="requires NVCHECKER_GITHUB_TOKEN, or it fails too much")]

async def test_github(get_version):
    assert await get_version("example", {"github": "harry-sanabria/ReleaseTestRepo"}) == "20140122.012101"

async def test_github_default_not_master(get_version):
    assert await get_version("example", {"github": "MariaDB/server"}) is not None

async def test_github_latest_release(get_version):
    assert await get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_latest_release": 1}) == "release3"

async def test_github_max_tag(get_version):
    assert await get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_max_tag": 1}) == "second_release"

async def test_github_max_tag_with_ignored_tags(get_version):
    assert await get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_max_tag": 1, "ignored_tags": "second_release release3"}) == "first_release"

async def test_github_max_tag_with_include(get_version):
    version = await get_version("example", {
        "github": "EFForg/https-everywhere",
        "use_max_tag": 1,
        "include_tags_pattern": r"^\d",
    })
    assert re.match(r'[\d.]+', version)
