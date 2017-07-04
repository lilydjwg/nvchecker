# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_cmd(get_version):
    assert await get_version("example", {"cmd": "echo Meow"}) == "Meow"

async def test_cmd_complex(get_version):
    assert await get_version("example", {"cmd": "echo Meow | sed 's/meow/woof/i'"}) == "woof"
