# MIT licensed
# Copyright (c) 2018 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = pytest.mark.asyncio

async def test_cache(get_version):
  a = await get_version("a", {"cmd": "date +%%Y-%%m-%%d"})
  b = await get_version("b", {"cmd": "date +%%Y-%%m-%%d"})
  c = await get_version("c", {"cmd": "date"})
  assert a == b
  assert a != c
