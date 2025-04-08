# MIT Licensed
# Copyright (c) 2024 Bert Peters <bertptrs@archlinux.org>, et al.
import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

@pytest.mark.flaky(reruns=10)
async def test_launchpad(get_version):
  version = await get_version(
    "sakura",
    {
      "source": "launchpad",
      "launchpad": "sakura",
    }
  )

  assert version.startswith('3.8.')
