# MIT licensed
# Copyright (c) 2024 Rocket Aaron <i@rocka.me>, et al.

import pytest

jq_available = True
try:
  import jq
except ImportError:
  jq_available = False

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.needs_net,
  pytest.mark.skipif(not jq_available, reason="needs jq"),
]

async def test_jq(get_version):
    ver = await get_version("aur", {
        "source": "jq",
        "url": "https://aur.archlinux.org/rpc/v5/info?arg[]=nvchecker-git"
    })
    ver = ver.strip()
    assert ver.startswith("{")
    assert ver.endswith("}")

async def test_jq_filter(get_version):
    ver = await get_version("aur", {
        "source": "jq",
        "url": "https://aur.archlinux.org/rpc/v5/info?arg[]=nvchecker-git",
        "filter": '.results[0].PackageBase',
    })
    assert ver == "nvchecker-git"
