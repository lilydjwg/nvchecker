# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_anitya(get_version):
  assert await get_version("shutter", {"anitya": "fedora/shutter"}) == "0.94.3"
