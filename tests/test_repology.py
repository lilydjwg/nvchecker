# MIT licensed
# Copyright (c) 2019-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio,
              pytest.mark.needs_net]

async def test_repology(get_version):
  assert await get_version("ssed", {
        "source": "repology",
        "repo": "aur",
  }) == "3.62"

async def test_repology_no_repo(get_version):
  try:
    assert await get_version("ssed", {
        "source": "repology",
    }) is None
  except RuntimeError as e:
    assert "repo field is required" in str(e)
