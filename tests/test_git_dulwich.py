# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <lorepirri@gmail.com>

import pytest

dulwich_available = True
try:
    import dulwich  # type: ignore[import-not-found]
except ImportError:
    dulwich_available = False

import os
try:
    import niquests
    conflicts = 'SSL_CERT_FILE' in os.environ
except ImportError:
    conflicts = False

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.needs_net,
    pytest.mark.skipif(not dulwich_available, reason="needs dulwich"),
    pytest.mark.skipif(conflicts, reason="dulwich conflicts with niquests via urllib3/urllib3.future when mitm proxy is used"),
]


async def test_git_dulwich(get_version):
    assert (
        await get_version(
            "example",
            {
                "source": "git_dulwich",
                "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
            },
        )
        == "v1.1.1"
    )


async def test_git_dulwich_commit(get_version):
    assert (
        await get_version(
            "example",
            {
                "source": "git_dulwich",
                "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
                "use_commit": True,
            },
        )
        == "ddd0f15ae83993f5cb66a927a28673882e99100b"
    )


async def test_git_dulwich_commit_branch(get_version):
    assert (
        await get_version(
            "example",
            {
                "source": "git_dulwich",
                "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
                "use_commit": True,
                "branch": "with-executables",
            },
        )
        == "6b8dc4a827797aa025ff6b8f425e583858a10d4f"
    )
