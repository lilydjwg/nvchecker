# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_combiner(run_str_multi):
  conf = r'''
[entry-1]
source = "cmd"
cmd = "echo 1"

[entry-2]
source = "cmd"
cmd = "echo 2"

[entry-3]
source = "combiner"
from = ["entry-1", "entry-2", "entry-2"]
format = "$1-$2-$3"
'''

  r = await run_str_multi(conf)
  assert r['entry-3'] == '1-2-2'
