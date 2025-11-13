# MIT licensed
# Copyright (c) 2024 Jakub Ružička <jru@debian.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_rpmrepo_fedora(get_version):
    ver = await get_version("knot_fedora-39", {
        "source": "rpmrepo",
        "pkg": "libbtrfs",
        "repo": "https://ftp.sh.cvut.cz/fedora/linux/updates/42/Everything/x86_64/",
    })
    assert ver.startswith("6.17")

async def test_rpmrepo_alma(get_version):
    assert await get_version("test", {
        "source": "rpmrepo",
        "pkg": "readline",
        "repo": "http://ftp.sh.cvut.cz/almalinux/9/BaseOS/x86_64/os/",
    }) == "8.1"
