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

async def test_github_commit_name(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_commit_name": True,
    }) == "20140122.012101+2b3cdf6134b07ae6ac77f11b586dc1ae6d1521db"

async def test_github_default_not_master(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "MariaDB/server",
    }) is not None

async def test_github_latest_release(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_latest_release": True,
    }) == "release3"

async def test_github_latest_release_commit_name(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_latest_release": True,
        "use_commit_name": True,
    }) == "release3+2b3cdf6134b07ae6ac77f11b586dc1ae6d1521db"

async def test_github_max_tag(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_tag": True,
    }) == "second_release"

async def test_github_max_tag_commit_name(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_tag": True,
        "use_commit_name": True,
    }) == "second_release+0f01b10ee72809e7ec0d903db95bcb6eef18c925"

async def test_github_max_tag_with_ignored(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_max_tag": True,
        "ignored": "second_release release3",
    }) == "first_release"

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

async def test_github_latest_tag(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_latest_tag": True,
    }) == "release3"

async def test_github_latest_tag_commit_name(get_version):
    assert await get_version("example", {
        "source": "github",
        "github": "harry-sanabria/ReleaseTestRepo",
        "use_latest_tag": True,
        "use_commit_name": True,
    }) == "release3+2b3cdf6134b07ae6ac77f11b586dc1ae6d1521db"

