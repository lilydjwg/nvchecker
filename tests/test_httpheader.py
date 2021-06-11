# MIT licensed
# Copyright (c) 2021 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
import pytest_httpbin
assert pytest_httpbin # for pyflakes

pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_redirection(get_version):
    assert await get_version("unifiedremote", {
        "source": "httpheader",
        "url": "https://www.unifiedremote.com/download/linux-x64-deb",
        "regex": r'urserver-([\d.]+).deb',
    }) is not None

async def test_get_version_withtoken(get_version, httpbin):
    assert await get_version("unifiedremote", {
        "source": "httpheader",
        "url": httpbin.url + "/basic-auth/username/superpassword",
        "httptoken": "Basic dXNlcm5hbWU6c3VwZXJwYXNzd29yZA==",
        "header": "server",
        "regex": r'([0-9.]+)*',
    }) is not None
