# MIT licensed
# Copyright (c) 2024 bgme <i@bgme.me>.

import pytest

from nvchecker.api import HTTPError

lxml_available = True
try:
    import lxml
except ImportError:
    lxml_available = False

pytestmark = [
    pytest.mark.asyncio(scope="session"),
    pytest.mark.needs_net,
    pytest.mark.skipif(not lxml_available, reason="needs lxml")
]


async def test_go(get_version):
    assert await get_version("one version", {
        "source": "go",
        "go": "github.com/caddyserver/replace-response",
    }) == "v0.0.0-20231221003037-a85d4ddc11d6"

    assert await get_version("multiple version", {
        "source": "go",
        "go": "github.com/corazawaf/coraza-caddy",
    }) == "v1.2.2"

    with pytest.raises(HTTPError):
        await get_version("not found", {
            "source": "go",
            "go": "github.com/asdas/sadfasdf",
        })
