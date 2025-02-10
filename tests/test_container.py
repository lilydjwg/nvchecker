# MIT licensed
# Copyright (c) 2020 Chih-Hsuan Yen <yan12125 at gmail dot com>

import os
import datetime

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net,
             pytest.mark.skipif(bool(os.environ.get('GITHUB_RUN_ID')), reason="400 very often")]

async def test_container(get_version):
  assert await get_version("hello-world", {
    "source": "container",
    "container": "library/hello-world",
    "include_regex": "linux",
  }) == "linux"

async def test_container_with_tag(get_version):
  update_time = await get_version("bitnami/mongodb:5.0", {
    "source": "container",
    "container": "bitnami/mongodb:5.0",
  })
  # the update time is changing occasionally, so we can not compare the exact time, otherwise the test will be failed in the future
  assert datetime.date.fromisoformat(update_time.split('T')[0]) > datetime.date(2023, 12, 1)

async def test_container_with_tag_and_multi_arch(get_version):
  update_time = await get_version("hello-world:linux", {
    "source": "container",
    "container": "library/hello-world:linux",
  })
  # the update time is changing occasionally, so we can not compare the exact time, otherwise the test will be failed in the future
  assert datetime.date.fromisoformat(update_time.split('T')[0]) > datetime.date(2023, 1, 1)

async def test_container_with_tag_and_registry(get_version):
  update_time = await get_version("hello-world-nginx:v1.0", {
    "source": "container",
    "registry": "quay.io",
    "container": "redhattraining/hello-world-nginx:v1.0",
  })
  # the update time probably won't be changed
  assert datetime.date.fromisoformat(update_time.split('T')[0]) == datetime.date(2019, 6, 26)

async def test_container_paging(get_version):
  assert await get_version("prometheus-operator", {
    "source": "container",
    "registry": "quay.io",
    "container": "redhattraining/hello-world-nginx",
  }) == "v1.0"
