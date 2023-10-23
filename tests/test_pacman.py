# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pathlib
import shutil
import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.skipif(shutil.which("pacman") is None,
                                 reason="requires pacman command"),
              pytest.mark.skipif(not pathlib.Path("/var/lib/pacman/sync/core.db").exists(),
                                 reason="requires synced pacman databases")]

async def test_pacman(get_version):
    assert await get_version("base", {
        "source": "pacman",
    }) == "3-2"

async def test_pacman_strip_release(get_version):
    assert await get_version("base", {
        "source": "pacman",
        "strip_release": 1,
    }) == "3"
