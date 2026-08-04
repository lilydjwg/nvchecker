# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest

pytestmark = pytest.mark.asyncio


@pytest.mark.needs_net
@pytest.mark.flaky(reruns=10)
async def test_gitea(get_version):
    ver = await get_version("example", {
        "source": "gitea",
        "gitea": "gitea/tea"})
    assert ver.startswith('20')
    assert 'T' in ver


@pytest.mark.needs_net
@pytest.mark.flaky(reruns=10)
async def test_gitea_max_tag_with_include(get_version):
    assert await get_version("example", {
        "source": "gitea",
        "gitea": "gitea/tea",
        "use_max_tag": True,
        "include_regex": r'v0\.9.*',
    }) == "v0.9.2"


@pytest.mark.needs_net
async def test_gitea_latest_release(get_version):
    ver = await get_version("example", {
        "source": "gitea",
        "host": "codeberg.org",
        "gitea": "ciberandy/qiv",
        "use_latest_release": True,
    })
    assert ver.startswith('v3.'), ver


async def test_gitea_max_tag_fetches_all_pages():
    from nvchecker_source import gitea

    class FakeCache:
        def __init__(self):
            self.urls = []

        async def get_json(self, url, *, headers):
            assert headers == {}
            self.urls.append(url)

            responses = {
                "https://gitea.example/api/v1/repos/owner/repo/tags?page=1": [
                    {
                        "name": "v2.0.0",
                        "id": "revision-2",
                    },
                ],
                "https://gitea.example/api/v1/repos/owner/repo/tags?page=2": [
                    {
                        "name": "v1.0.0",
                        "id": "revision-1",
                    },
                ],
                "https://gitea.example/api/v1/repos/owner/repo/tags?page=3": [],
            }
            return responses[url]

    class FakeKeyManager:
        def get_key(self, host, key):
            assert host == "gitea.example"
            assert key == "gitea_gitea.example"
            return None

    cache = FakeCache()

    result = await gitea.get_version(
        "example",
        {
            "source": "gitea",
            "host": "gitea.example",
            "gitea": "owner/repo",
            "use_max_tag": True,
        },
        cache=cache,
        keymanager=FakeKeyManager(),
    )

    assert [tag.version for tag in result] == [
        "v2.0.0",
        "v1.0.0",
    ]
    assert [tag.revision for tag in result] == [
        "revision-2",
        "revision-1",
    ]
    assert [tag.url for tag in result] == [
        "https://gitea.example/owner/repo/releases/tag/v2.0.0",
        "https://gitea.example/owner/repo/releases/tag/v1.0.0",
    ]
    assert cache.urls == [
        "https://gitea.example/api/v1/repos/owner/repo/tags?page=1",
        "https://gitea.example/api/v1/repos/owner/repo/tags?page=2",
        "https://gitea.example/api/v1/repos/owner/repo/tags?page=3",
    ]
