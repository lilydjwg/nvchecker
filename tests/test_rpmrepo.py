# MIT licensed
# Copyright (c) 2024 Jakub Ružička <jru@debian.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_rpmrepo_fedora(get_version):
    assert await get_version("knot_fedora-39", {
        "source": "rpmrepo",
        "pkg": "knot",
        "repo": "http://ftp.sh.cvut.cz/fedora/linux/updates/39/Everything/x86_64/",
    }) == "3.3.9"

async def test_rpmrepo_alma(get_version):
    assert await get_version("knot_fedora-39", {
        "source": "rpmrepo",
        "pkg": "tmux",
        "repo": "http://ftp.sh.cvut.cz/almalinux/9.5/BaseOS/x86_64/os/",
    }) == "3.2a"
