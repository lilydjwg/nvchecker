# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.needs_net,
              pytest.mark.skipif("NVCHECKER_GITLAB_TOKEN_GITLAB_COM" not in os.environ,
                                 reason="requires NVCHECKER_GITLAB_TOKEN_GITLAB_COM")]

async def test_gitlab(get_version):
    ver = await get_version("example",
                            {"gitlab": "gitlab-org/gitlab-test"})
    assert len(ver) == 8
    assert ver.isdigit()

async def test_gitlab_max_tag(get_version):
    assert await get_version("example", {"gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1}) == "v1.1.1"

async def test_gitlab_max_tag_with_ignored_tags(get_version):
    assert await get_version("example", {"gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1, "ignored_tags": "v1.1.0 v1.1.1"}) == "v1.0.0"

async def test_gitlab_max_tag_with_include(get_version):
    assert await get_version("example", {
        "gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1,
        "include_regex": r'v1\.0.*',
    }) == "v1.0.0"

async def test_gitlab_max_tag_with_ignored(get_version):
    assert await get_version("example", {
        "gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1,
        "ignored": "v1.1.0 v1.1.1",
    }) == "v1.0.0"

