# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import os

from flaky import flaky
import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.needs_net,
              pytest.mark.skipif(os.environ.get('TRAVIS') == 'true',
                                 reason="fail too often")]

@flaky(max_runs=10)
async def test_aur(get_version):
    assert await get_version("ssed", {
        "source": "aur",
    }) == "3.62-2"

@flaky(max_runs=10)
async def test_aur_strip_release(get_version):
    assert await get_version("ssed", {
        "source": "aur",
        "strip_release": 1,
    }) == "3.62"

@flaky(max_runs=10)
async def test_aur_use_last_modified(get_version):
    assert await get_version("ssed", {
        "source": "aur",
        'use_last_modified': True,
    }) == "3.62-2-20150725052412"
