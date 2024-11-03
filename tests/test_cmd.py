# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import time
import pytest
pytestmark = pytest.mark.asyncio

async def test_cmd(get_version):
    assert await get_version("example", {
        "source": "cmd",
        "cmd": "echo Meow",
    }) == "Meow"

async def test_cmd_complex(get_version):
    assert await get_version("example", {
        "source": "cmd",
        "cmd": "echo Meow | sed 's/meow/woof/i'",
    }) == "woof"

async def test_cmd_with_percent(run_str):
    test_conf = '''\
[example]
source = "cmd"
cmd = "date +%Y-%m-%d"'''
    date = await run_str(test_conf)
    expected = time.strftime('%Y-%m-%d')
    assert date == expected

