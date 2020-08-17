# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_packagist(get_version):
    assert await get_version("butterfly/example-web-application", {"packagist": None}) == "1.2.0"
