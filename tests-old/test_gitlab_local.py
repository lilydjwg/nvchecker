# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import pytest
import contextlib
pytestmark = [pytest.mark.asyncio,
              pytest.mark.needs_net,
              pytest.mark.skipif(os.environ.get('TRAVIS') == 'true',
                                 reason="rate-limited per IP")]

@contextlib.contextmanager
def unset_gitlab_token_env():
  token = os.environ.get('NVCHECKER_GITLAB_TOKEN_GITLAB_COM')
  try:
    if token:
      del os.environ['NVCHECKER_GITLAB_TOKEN_GITLAB_COM']
    yield token
  finally:
    if token:
      os.environ['NVCHECKER_GITLAB_TOKEN_GITLAB_COM'] = token

async def test_gitlab(get_version):
    with unset_gitlab_token_env():
        ver = await get_version("example",
                                {"gitlab": "gitlab-org/gitlab-test"})
        assert len(ver) == 8
        assert ver.isdigit()

async def test_gitlab_max_tag(get_version):
    with unset_gitlab_token_env():
        assert await get_version("example", {"gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1}) == "v1.1.1"

async def test_gitlab_max_tag_with_ignored_tags(get_version):
    with unset_gitlab_token_env():
        ver = await get_version("example",
                                {"gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1, "ignored_tags": "v1.1.0 v1.1.1"})
        assert ver == "v1.0.0"

