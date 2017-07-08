# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from flaky import flaky
import pytest
pytestmark = pytest.mark.asyncio

@flaky
async def test_aur(get_version):
    assert await get_version("asciidoc-fake", {"aur": None}) == "1.0-1"

@flaky
async def test_aur_strip_release(get_version):
    assert await get_version("asciidoc-fake", {"aur": None, "strip-release": 1}) == "1.0"
