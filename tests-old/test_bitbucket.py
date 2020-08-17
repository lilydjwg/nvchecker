# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_bitbucket(get_version):
    assert await get_version("example", {"bitbucket": "prawee/git-tag"}) == "20150303"

async def test_bitbucket_max_tag(get_version):
    assert await get_version("example", {"bitbucket": "prawee/git-tag", "use_max_tag": 1}) == "1.7.0"

async def test_bitbucket_max_tag_with_ignored_tags(get_version):
    assert await get_version("example", {"bitbucket": "prawee/git-tag", "use_max_tag": 1, "ignored_tags": "1.6.0 1.7.0"}) == "v1.5"
