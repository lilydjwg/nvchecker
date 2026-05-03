# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <lorepirri@gmail.com>

import pytest

# Skip all tests in this file if pygit2 is not installed
pygit2_available = True
try:
  import pygit2
except ImportError:
  pygit2_available = False

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.needs_net,
  pytest.mark.skipif(not pygit2_available, reason="needs pygit2"),
]


async def test_git_pygit2(get_version):
    assert await get_version("example", {
        "source": "git_pygit2",
        "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
    }) == "v1.1.1"


async def test_git_pygit2_commit(get_version):
    assert await get_version("example", {
        "source": "git_pygit2",
        "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
        "use_commit": True,
    }) == "ddd0f15ae83993f5cb66a927a28673882e99100b"


async def test_git_pygit2_commit_branch(get_version):
    assert await get_version("example", {
        "source": "git_pygit2",
        "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
        "use_commit": True,
        "branch": "with-executables",
    }) == "6b8dc4a827797aa025ff6b8f425e583858a10d4f"

