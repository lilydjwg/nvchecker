# MIT licensed
# Copyright (c) 2020 Chih-Hsuan Yen <yan12125 at gmail dot com>

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_container(get_version):
  assert await get_version("hello-world", {
    "source": "container",
    "container": "library/hello-world",
    "include_regex": "linux",
  }) == "linux"

async def test_container_paging(get_version):
  assert await get_version("prometheus-operator", {
    "source": "container",
    "registry": "quay.io",
    "container": "redhattraining/hello-world-nginx",
  }) == "v1.0"
