# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import time
import pytest
pytestmark = pytest.mark.asyncio

async def test_cmd(get_version):
    assert await get_version("example", {"cmd": "echo Meow"}) == "Meow"

async def test_cmd_complex(get_version):
    assert await get_version("example", {"cmd": "echo Meow | sed 's/meow/woof/i'"}) == "woof"

async def test_cmd_with_percent(run_source):
    test_conf = '''\
[example]
cmd = date +%Y-%m-%d'''
    date = await run_source(test_conf)
    expected = time.strftime('%Y-%m-%d')
    assert date == expected

