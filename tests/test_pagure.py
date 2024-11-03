# MIT licensed
# Copyright (c) 2020 Felix Yan <felixonmars@archlinux.org>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_pagure(get_version):
    ver = await get_version("example", {
        "source": "pagure",
        "pagure": "nvchecker-test",
    })
    assert ver == "0.2"

async def test_pagure_with_ignored(get_version):
    ver = await get_version("example", {
        "source": "pagure",
        "pagure": "nvchecker-test",
        "ignored": "0.2",
    })
    assert ver == "0.1"

async def test_pagure_with_alternative_host(get_version):
    ver = await get_version("example", {
        "source": "pagure",
        "pagure": "rpms/glibc",
        "host": "src.fedoraproject.org",
        "include_regex": r"F-\d+-start",
    })
    assert ver == "F-13-start"
