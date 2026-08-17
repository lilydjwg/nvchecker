# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

from unittest.mock import AsyncMock

import pytest

from nvchecker_source import pypi

pytestmark = pytest.mark.asyncio


@pytest.mark.needs_net
async def test_pypi(get_version):
    assert await get_version("example", {
        "source": "pypi",
    }) == "0.1.0"


@pytest.mark.needs_net
async def test_pypi_release(get_version):
    assert await get_version("example-test-package", {
        "source": "pypi",
        "pypi": "example-test-package",
    }) == "1.0.0"


@pytest.mark.needs_net
async def test_pypi_pre_release(get_version):
    assert await get_version("example-test-package", {
        "source": "pypi",
        "use_pre_release": 1,
    }) == "1.0.1a1"


@pytest.mark.needs_net
async def test_pypi_list(get_version):
    assert await get_version("urllib3", {
        "source": "pypi",
        "include_regex": "^1\\..*",
    }) == "1.26.20"


@pytest.mark.needs_net
async def test_pypi_invalid_version(get_version):
    await get_version("sympy", {
        "source": "pypi",
    })


@pytest.mark.needs_net
async def test_pypi_yanked_version(get_version):
    assert await get_version("urllib3", {
        "source": "pypi",
        "include_regex": "^(1\\..*)|(2\\.0\\.[0,1])",
    }) == "1.26.20"


@pytest.mark.needs_net
async def test_pypi_changelog(get_result):
    result = await get_result("example", {
        "source": "pypi",
    })

    assert result.changelog_url == None


@pytest.mark.needs_net
async def test_pypi_no_changelog(get_result):
    result = await get_result("numpy", {
        "source": "pypi",
    })

    assert result.changelog_url.startswith('https://numpy.org')


async def test_pypi_creation_time():
    cache = AsyncMock()
    cache.get_json.return_value = {
        "info": {"project_urls": {}},
        "releases": {
            "1.0.0": [
                {
                    "yanked": False,
                    "upload_time_iso_8601":
                        "2024-01-02T03:04:05.000000Z",
                },
            ],
        },
    }

    results = await pypi.get_version(
        "example",
        {"source": "pypi"},
        cache=cache,
    )

    assert len(results) == 1

    result = results[0]
    assert result.version == "1.0.0"
    assert result.url == "https://pypi.org/project/example/1.0.0/"
    assert result.gitref is None
    assert result.revision is None
    assert (
        result.creation_time
        == "2024-01-02T03:04:05.000000Z"
    )
    assert result.revision_creation_time is None

    cache.get_json.assert_awaited_once_with(
        "https://pypi.org/pypi/example/json",
    )


async def test_pypi_creation_time_uses_earliest_file():
    cache = AsyncMock()
    cache.get_json.return_value = {
        "info": {"project_urls": {}},
        "releases": {
            "1.0.0": [
                {
                    "yanked": False,
                    "upload_time_iso_8601":
                        "2024-01-02T03:04:09.000000Z",
                },
                {
                    "yanked": False,
                    "upload_time_iso_8601":
                        "2024-01-02T03:04:05.000000Z",
                },
                {
                    "yanked": False,
                    "upload_time_iso_8601":
                        "2024-01-02T03:04:07.000000Z",
                },
            ],
        },
    }

    results = await pypi.get_version(
        "example",
        {"source": "pypi"},
        cache=cache,
    )

    assert len(results) == 1
    assert (
        results[0].creation_time
        == "2024-01-02T03:04:05.000000Z"
    )


async def test_pypi_creation_time_ignores_missing_timestamps():
    cache = AsyncMock()
    cache.get_json.return_value = {
        "info": {"project_urls": {}},
        "releases": {
            "1.0.0": [
                {
                    "yanked": False,
                },
                {
                    "yanked": False,
                    "upload_time_iso_8601":
                        "2024-01-02T03:04:05.000000Z",
                },
            ],
        },
    }

    results = await pypi.get_version(
        "example",
        {"source": "pypi"},
        cache=cache,
    )

    assert len(results) == 1
    assert (
        results[0].creation_time
        == "2024-01-02T03:04:05.000000Z"
    )


@pytest.mark.parametrize("release_files", [
    [],
    [
        {
            "yanked": False,
        },
    ],
])
async def test_pypi_creation_time_unavailable(release_files):
    cache = AsyncMock()
    cache.get_json.return_value = {
        "info": {"project_urls": {}},
        "releases": {
            "1.0.0": release_files,
        },
    }

    results = await pypi.get_version(
        "example",
        {"source": "pypi"},
        cache=cache,
    )

    assert len(results) == 1
    assert results[0].version == "1.0.0"
    assert results[0].creation_time is None
    assert results[0].revision_creation_time is None
