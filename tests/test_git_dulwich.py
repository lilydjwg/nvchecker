# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <lorepirri@gmail.com>

from types import SimpleNamespace

import pytest

dulwich_available = True
try:
    from nvchecker_source import git_dulwich
except ImportError:
    dulwich_available = False


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(not dulwich_available, reason="needs dulwich"),
]


@pytest.mark.needs_net
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


@pytest.mark.needs_net
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


@pytest.mark.needs_net
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


async def test_git_dulwich_http_auth(monkeypatch):

    expected_password = "secret-token"

    class FakeKeyManager:
        def get_key(self, name):
            assert name == "private-repository"
            return expected_password

    class FakeClient:
        def get_refs(self, path):
            assert path == "/owner/repository.git"
            return SimpleNamespace(
                refs={
                    b"refs/tags/v1.0.0": b"0123456789abcdef",
                }
            )

    def fake_get_transport_and_path(
        location,
        *,
        config,
        username=None,
        password=None,
        **kwargs,
    ):
        assert location == "https://example.com/owner/repository.git"
        assert username == "git-user"
        assert password == expected_password
        return FakeClient(), "/owner/repository.git"

    monkeypatch.setattr(
        git_dulwich.dulwich.client,
        "get_transport_and_path",
        fake_get_transport_and_path,
    )

    class FakeCache:
        async def get(self, key, callback):
            assert key == (
                "https://example.com/owner/repository.git",
                None,
                "git-user",
                expected_password,
            )
            return await callback(key)

    result = await git_dulwich.get_version(
        "example",
        {
            "source": "git_dulwich",
            "git": "https://example.com/owner/repository.git",
            "username": "git-user",
            "password_key": "private-repository",
        },
        cache=FakeCache(),
        keymanager=FakeKeyManager(),
    )

    assert result[0].version == "v1.0.0"
