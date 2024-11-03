# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_cratesio(get_version):
    assert await get_version("example", {
        "source": "cratesio",
    }) == "1.1.0"

async def test_cratesio_list(get_version):
    assert await get_version("example", {
        "source": "cratesio",
        "include_regex": r"^1\.0.*",
    }) == "1.0.2"

async def test_cratesio_skip_prerelease(get_version):
    with pytest.raises(RuntimeError, match='include_regex matched no versions'):
        await get_version("cargo-lock", {
            "source": "cratesio",
            "include_regex": r".*-.*",
        })

async def test_cratesio_use_prerelease(get_version):
    await get_version("cargo-lock", {
        "source": "cratesio",
        "use_pre_release": "true",
        "include_regex": r".*-.*",
    })
