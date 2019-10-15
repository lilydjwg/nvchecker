# MIT licensed
# Copyright (c) 2018 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import tempfile
import contextlib

from nvchecker.source import HTTPError

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@contextlib.contextmanager
def unset_github_token_env():
  token = os.environ.get('NVCHECKER_GITHUB_TOKEN')
  try:
    if token:
      del os.environ['NVCHECKER_GITHUB_TOKEN']
    yield token
  finally:
    if token:
      os.environ['NVCHECKER_GITHUB_TOKEN'] = token

async def test_keyfile_missing(run_source):
  test_conf = '''\
[example]
github = harry-sanabria/ReleaseTestRepo
'''

  assert await run_source(test_conf) in ['20140122.012101', None]

async def test_keyfile_invalid(run_source):
  with tempfile.NamedTemporaryFile(mode='w') as f, \
    unset_github_token_env():
    f.write('''\
[keys]
github = xxx
            ''')
    f.flush()
    test_conf = '''\
[example]
github = harry-sanabria/ReleaseTestRepo

[__config__]
keyfile = {name}
'''.format(name=f.name)

    try:
      version = await run_source(test_conf, clear_cache=True)
      assert version is None # out of allowance
      return
    except HTTPError as e:
      assert e.code == 401
      return

    raise Exception('expected 401 response')

@pytest.mark.skipif('NVCHECKER_GITHUB_TOKEN' not in os.environ,
                    reason='no key given')
async def test_keyfile_valid(run_source):
  with tempfile.NamedTemporaryFile(mode='w') as f, \
    unset_github_token_env() as token:
    f.write('''\
[keys]
github = {token}
            '''.format(token=token))
    f.flush()

    test_conf = '''\
[example]
github = harry-sanabria/ReleaseTestRepo

[__config__]
keyfile = {name}
      '''.format(name=f.name)

    assert await run_source(test_conf) == '20140122.012101'
