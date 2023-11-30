# MIT licensed
# Copyright (c) 2020 Chih-Hsuan Yen <yan12125 at gmail dot com>

import pytest
import datetime
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_container(get_version):
  assert await get_version("hello-world", {
    "source": "container",
    "container": "library/hello-world",
    "include_regex": "linux",
  }) == "linux"

async def test_container_with_tag(get_version):
  update_time = await get_version("hello-world:linux", {
    "source": "container",
    "container": "library/hello-world:linux",
  })
  # the update time is changing occasionally, so we can not compare the exact time, otherwise the test will be failed in the future
  assert datetime.datetime.fromisoformat(update_time).date() > datetime.date(2023, 1, 1)

async def test_container_with_tag_and_registry(get_version):
  update_time = await get_version("hello-world-nginx:v1.0", {
    "source": "container",
    "registry": "quay.io",
    "container": "redhattraining/hello-world-nginx:v1.0",
  })
  # the update time probably won't be changed
  assert datetime.datetime.fromisoformat(update_time).date() == datetime.date(2019, 6, 26)

async def test_container_paging(get_version):
  assert await get_version("prometheus-operator", {
    "source": "container",
    "registry": "quay.io",
    "container": "redhattraining/hello-world-nginx",
  }) == "v1.0"
