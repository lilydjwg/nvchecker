# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import time
import pytest
pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(("cmd", "expected"), [
        ("echo Meow", "Meow"),
        ("echo ' Meow '", "Meow"),
        ("echo -e '3.2\n4.5'", "4.5"),
        ("echo -e '1.1\n 1.3\t\t\n1.0\t'", "1.3"),
        ("echo -e '1.7\n\n\n    \n\n1.5'", "1.7"),
    ])
async def test_cmd(get_version, cmd, expected):
    assert await get_version("example", {
        "source": "cmd",
        "cmd": cmd,
    }) == expected

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
