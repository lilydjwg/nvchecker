# MIT licensed
# Copyright (c) 2020 lilydjwg <lilydjwg@gmail.com>, et al.
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import re

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_anitya(get_version):
  version = await get_version("shutter", {
    "source": "anitya",
    "anitya": "fedora/shutter",
  })
  assert re.match(r"[0-9.]+", version)

async def test_anitya_by_id(get_version):
  version = await get_version("shutter", {
    "source": "anitya",
    "anitya_id": "4813",
  })
  assert re.match(r"[0-9.]+", version)
