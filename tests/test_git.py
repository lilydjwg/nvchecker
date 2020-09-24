# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_git(get_version):
    assert await get_version("example", {
        "source": "git",
        "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
    }) == "v1.1.1"
