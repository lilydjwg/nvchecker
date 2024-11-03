# MIT licensed
# Copyright (c) 2024 bgme <i@bgme.me>.

import pytest

from nvchecker.api import HTTPError

try:
  import lxml
  lxml_available = True
except ImportError:
  lxml_available = False

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.needs_net,
  pytest.mark.skipif(not lxml_available, reason="needs lxml")
]


async def test_go(get_version):
  ver = await get_version("one version", {
    "source": "go",
    "go": "github.com/caddyserver/replace-response",
  })

  assert ver.startswith("v0.0.0-")

  assert await get_version("multiple version", {
    "source": "go",
    "go": "github.com/corazawaf/coraza-caddy",
  }) == "v1.2.2"

  with pytest.raises(HTTPError):
    await get_version("not found", {
      "source": "go",
      "go": "github.com/asdas/sadfasdf",
    })
