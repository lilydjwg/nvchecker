# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest

httpbin_available = True
try:
  import pytest_httpbin
  assert pytest_httpbin # for pyflakes
except ImportError:
  httpbin_available = False

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

@pytest.mark.skipif(not httpbin_available, reason="needs pytest_httpbin")
async def test_cache_request_context(run_str_multi, httpbin):
  conf = rf'''
[plain]
source = "regex"
url = "{httpbin.url}/uuid"
regex = '"uuid":\s*"([0-9a-f-]+)"'

[other-ua]
source = "regex"
url = "{httpbin.url}/uuid"
regex = '"uuid":\s*"([0-9a-f-]+)"'
user_agent = "nvchecker-test"

[other-tries]
source = "regex"
url = "{httpbin.url}/uuid"
regex = '"uuid":\s*"([0-9a-f-]+)"'
tries = 2
'''

  r = await run_str_multi(conf)
  assert len(set(r.values())) == 3
