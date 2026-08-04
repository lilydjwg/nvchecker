# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_gitlab(get_version):
    ver = await get_version("example", {
        "source": "gitlab",
        "gitlab": "gitlab-org/gitlab-test",
    })
    assert len(ver) == 8
    assert ver.isdigit()

async def test_gitlab_blm(get_version):
    # repo with a custom main branch
    ver = await get_version("example", {
        "source": "gitlab",
        "gitlab": "asus-linux/asusctl",
    })
    assert len(ver) == 8
    assert ver.isdigit()

async def test_gitlab_max_tag(get_version):
    assert await get_version("example", {
        "source": "gitlab",
        "gitlab": "gitlab-org/gitlab-test",
        "use_max_tag": True,
    }) == "v1.1.1"

async def test_gitlab_max_tag_with_include(get_version):
    assert await get_version("example", {
        "source": "gitlab",
        "gitlab": "gitlab-org/gitlab-test",
        "use_max_tag": True,
        "include_regex": r'v1\.0.*',
    }) == "v1.0.0"

async def test_gitlab_max_tag_with_ignored(get_version):
    assert await get_version("example", {
        "source": "gitlab",
        "gitlab": "gitlab-org/gitlab-test",
        "use_max_tag": True,
        "ignored": "v1.1.0 v1.1.1",
    }) == "v1.0.0"

async def test_gitlab_revision_creation_time(get_result):
    result = await get_result("example", {
        "source": "gitlab",
        "gitlab": "gitlab-org/gitlab-test",
    })

    assert result.version == "20190625"
    assert result.revision is not None
    assert result.creation_time is None
    assert (
        result.revision_creation_time
        == "2019-06-25T23:59:19.000+00:00"
    )

async def test_gitlab_max_tag_timestamps(get_result):
    result = await get_result("example", {
        "source": "gitlab",
        "gitlab": "gitlab-org/gitlab-test",
        "use_max_tag": True,
    })

    assert result.version == "v1.1.1"
    assert result.gitref == "refs/tags/v1.1.1"
    assert (
        result.revision
        == "189a6c924013fc3fe40d6f1ec1dc20214183bc97"
    )
    assert result.creation_time == "2019-11-20T14:56:20.000Z"
    assert (
        result.revision_creation_time
        == "2019-10-11T18:06:49.000+02:00"
    )
