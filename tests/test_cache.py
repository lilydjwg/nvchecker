# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_cache(run_str_multi):
  conf = r'''
[cache-1]
source = "cmd"
cmd = "bash -c 'echo $RANDOM'"

[cache-2]
source = "cmd"
cmd = "bash -c 'echo $RANDOM'"
'''

  r = await run_str_multi(conf)
  assert r['cache-1'] == r['cache-2']
