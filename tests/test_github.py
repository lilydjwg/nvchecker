# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import re

import pytest

pytestmark = [pytest.mark.asyncio,
              pytest.mark.needs_net,
              pytest.mark.usefixtures('keyfile')]

async def test_github(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
    }) == "20140122.012101"

async def test_github_default_not_master(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "MariaDB/server",
    }) is not None

async def test_github_latest_release(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "dpeukert/ReleaseTestRepo",
        "use_latest_release": True,
    }) == "v0.0.0"

async def test_github_latest_release_include_prereleases(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "dpeukert/ReleaseTestRepo",
        "use_latest_release": True,
        "include_prereleases": True,
    }) == "v0.0.1-pre"

async def test_github_max_tag(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_tag": True,
    }) == "second_release"

async def test_github_max_release(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_release": True,
    }) == "second_release"

    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_release": True,
        "use_release_name": True,
    }) == "second_release"

async def test_github_max_tag_with_ignored(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_tag": True,
        "ignored": "second_release release3",
    }) == "first_release"

async def test_github_max_release_with_ignored(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_release": True,
        "ignored": "second_release release3",
    }) == "first_release"
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_release": True,
        "ignored": "second_release",
        "use_release_name": True,
    }) == "release #3"

async def test_github_with_path(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "petronny/ReleaseTestRepo",
        "path": "test_directory",
    }) == "20140122.012101"

async def test_github_with_path_and_branch(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "petronny/ReleaseTestRepo",
        "branch": "test",
        "path": "test_directory/test_directory",
    }) == "20190128.113201"

async def test_github_max_tag_with_include(get_version):
    version = await get_version("example", {
        "source": "github",
        "github": "EFForg/https-everywhere",
        "use_max_tag": True,
        "include_regex": r"chrome-\d.*",
    })
    assert re.match(r'chrome-[\d.]+', version)

async def test_github_max_release_with_include(get_version):
    version = await get_version("example", {
        "source": "github",
        "github": "EFForg/https-everywhere",
        "use_max_release": True,
        "use_release_name": True,
        "include_regex": r"Release \d.*",
    })
    assert re.match(r'Release [\d.]+', version)

async def test_github_latest_tag(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_latest_tag": True,
    }) == "release3"

async def test_github_latest_tag_revision_creation_time(get_result):
    result = await get_result("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_latest_tag": True,
    })

    assert result.version == "release3"
    assert result.gitref == "refs/tags/release3"
    assert result.revision == "2b3cdf6134b07ae6ac77f11b586dc1ae6d1521db"
    assert result.creation_time is None
    assert result.revision_creation_time == "2014-01-22T01:21:01Z"

async def test_github_revision_creation_time(get_result):
    result = await get_result("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
    })

    assert result.version == "20140122.012101"
    assert result.revision is not None
    assert result.creation_time is None
    assert result.revision_creation_time == "2014-01-22T01:21:01Z"

async def test_github_latest_release_creation_time(get_result):
    result = await get_result("example", {
        "source": "github",
        "github": "dpeukert/ReleaseTestRepo",
        "use_latest_release": True,
    })

    assert result.version == "v0.0.0"
    assert result.creation_time == "2023-08-25T21:05:58Z"
    assert result.revision_creation_time is None

async def test_github_latest_release_include_prereleases_timestamps(
    get_result,
):
    result = await get_result("example", {
        "source": "github",
        "github": "dpeukert/ReleaseTestRepo",
        "use_latest_release": True,
        "include_prereleases": True,
    })

    assert result.version == "v0.0.1-pre"
    assert result.creation_time == "2023-08-25T21:06:44Z"
    assert result.revision == "626bc187f3ee2d44d1931754bf8e3a55070c3526"
    assert result.revision_creation_time == "2023-08-25T21:06:20Z"

async def test_github_max_release_creation_time(get_result):
    result = await get_result("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_release": True,
    })

    assert result.version == "second_release"
    assert result.creation_time == "2014-01-21T19:29:56Z"
    assert result.revision_creation_time is None
