# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import shutil
import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.skipif(shutil.which("pacman") is None,
                                 reason="requires pacman command")]

async def test_pacman(get_version):
    assert await get_version("ipw2100-fw", {"pacman": None}) == "1.3-9"

async def test_pacman_strip_release(get_version):
    assert await get_version("ipw2100-fw", {"pacman": None, "strip-release": 1}) == "1.3"

async def test_pacman_numbered(get_version):
    assert await get_version("ipw2100-fw:1", {"pacman": None}, clear_cache=True) == "1.3-9"
