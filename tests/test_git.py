# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_git(get_version):
    assert await get_version("example", {
        "source": "git",
        "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
    }) == "v1.1.1"

async def test_git_commit(get_version):
    assert await get_version("example", {
        "source": "git",
        "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
        "use_commit": True,
    }) == "ddd0f15ae83993f5cb66a927a28673882e99100b"

async def test_git_commit_branch(get_version):
    assert await get_version("example", {
        "source": "git",
        "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
        "use_commit": True,
        "branch": "with-executables",
    }) == "6b8dc4a827797aa025ff6b8f425e583858a10d4f"
