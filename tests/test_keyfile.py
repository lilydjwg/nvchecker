# MIT licensed
# Copyright (c) 2018 lilydjwg <lilydjwg@gmail.com>, et al.

import tempfile

from nvchecker.source import HTTPError

import pytest
pytestmark = [pytest.mark.asyncio]

async def test_keyfile_missing(run_source):
  test_conf = '''\
[example]
github = harry-sanabria/ReleaseTestRepo
'''

  assert await run_source(test_conf) == '20140122.012101'

async def test_keyfile_invalid(run_source):
  with tempfile.NamedTemporaryFile(mode='w+') as f:
    f.write('''\
[keys]
github = xxx
            ''')
    f.flush()
    test_conf = f'''\
[example]
github = harry-sanabria/ReleaseTestRepo

[__config__]
keyfile = {f.name}
      '''

    try:
      await run_source(test_conf)
    except HTTPError as e:
      assert e.code == 401
