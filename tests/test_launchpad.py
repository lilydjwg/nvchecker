# MIT Licensed
# Copyright (c) 2024 Bert Peters <bertptrs@archlinux.org>, et al.
import pytest
pytestmark = [pytest.mark.asyncio(scope="session"), pytest.mark.needs_net]

async def test_launchpad(get_version):
  version = await get_version(
    "sakura",
    {
      "source": "launchpad",
      "launchpad": "sakura",
    }
  )

  assert version == '3.8.8'
