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

