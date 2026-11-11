# MIT licensed
# Copyright (c) 2026 Lorenzo Pirritano <lorepirri@gmail.com>

import pytest

from nvchecker.api import GetVersionError

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


class OldRemote:
    def ls_remotes(self, callbacks=None):
        assert callbacks is None
        return [
            {"name": "refs/tags/v1.0", "oid": "abc123"},
            {"name": "refs/heads/main", "oid": "def456"},
        ]


class NewRef:
    name = "refs/tags/v1.0"
    oid = "abc123"


class NewRemote:
    def list_heads(self, callbacks=None):
        assert callbacks is None
        return [NewRef()]


async def test_git_pygit2_list_heads_old_pygit2_shape():
    from nvchecker_source.git_pygit2 import _list_heads

    refs = _list_heads(OldRemote())

    assert refs[0].name == "refs/tags/v1.0"
    assert refs[0].oid == "abc123"

    assert refs[1].name == "refs/heads/main"
    assert refs[1].oid == "def456"


async def test_git_pygit2_list_heads_new_pygit2_shape():
    from nvchecker_source.git_pygit2 import _list_heads

    refs = _list_heads(NewRemote())

    assert refs[0].name == "refs/tags/v1.0"
    assert refs[0].oid == "abc123"


async def test_git_pygit2(get_version):
    assert (
        await get_version(
            "example",
            {
                "source": "git_pygit2",
                "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
            },
        )
        == "v1.1.1"
    )


async def test_git_pygit2_commit(get_version):
    assert (
        await get_version(
            "example",
            {
                "source": "git_pygit2",
                "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
                "use_commit": True,
            },
        )
        == "ddd0f15ae83993f5cb66a927a28673882e99100b"
    )


async def test_git_pygit2_commit_branch(get_version):
    assert (
        await get_version(
            "example",
            {
                "source": "git_pygit2",
                "git": "https://gitlab.com/gitlab-org/gitlab-test.git",
                "use_commit": True,
                "branch": "with-executables",
            },
        )
        == "6b8dc4a827797aa025ff6b8f425e583858a10d4f"
    )


async def test_git_pygit2_http_auth(monkeypatch):
    from nvchecker_source import git_pygit2

    expected_password = "secret-token"

    class FakeKeyManager:
        def get_key(self, name):
            assert name == "private-repository"
            return expected_password

    class FakeRemote:
        def list_heads(self, callbacks=None):
            assert callbacks is not None

            credentials = callbacks.credentials
            assert isinstance(credentials, pygit2.UserPass)
            # credential_tuple is part of pygit2's public API and is available across
            # the supported pygit2 versions. Avoid asserting on the private _username
            # and _password attributes.
            assert credentials.credential_tuple == (
                "git-user",
                expected_password,
            )
            return [NewRef()]

    class FakeRemotes:
        def create_anonymous(self, url):
            assert url == "https://example.com/owner/repository.git"
            return FakeRemote()

    class FakeRepo:
        remotes = FakeRemotes()

    monkeypatch.setattr(
        git_pygit2.pygit2,
        "init_repository",
        lambda path, bare: FakeRepo(),
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

    result = await git_pygit2.get_version(
        "example",
        {
            "source": "git_pygit2",
            "git": "https://example.com/owner/repository.git",
            "username": "git-user",
            "password_key": "private-repository",
        },
        cache=FakeCache(),
        keymanager=FakeKeyManager(),
    )

    assert result[0].version == "v1.0"


@pytest.mark.parametrize(
    "conf",
    [
        {
            "git": "https://example.com/repository.git",
            "username": "git-user",
        },
        {
            "git": "https://example.com/repository.git",
            "password_key": "git-password",
        },
    ],
)
async def test_git_pygit2_http_auth_requires_both_options(conf):
    from nvchecker_source import git_pygit2

    with pytest.raises(
        GetVersionError,
        match="username and password_key must be specified together",
    ):
        await git_pygit2.get_version(
            "test",
            conf,
            cache=None,
            keymanager=None,
        )
