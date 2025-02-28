# MIT licensed
# Copyright (c) 2025 Maxim Slipenko <maxim@slipenko.com>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_snapcraft(get_version):
    assert await get_version("test", {
        "source": "snapcraft",
        "snap": "test-snapd-public",
        "channel": "edge",
    }) == "2.0"

async def test_snapcraft_non_existent_snap(get_version):
    with pytest.raises(RuntimeError, match='Failed to request snap info for not-existent-snap'):
        assert await get_version("test", {
            "source": "snapcraft",
            "snap": "not-existent-snap",
            "channel": "stable",
        })

async def test_snapcraft_non_existent_channel(get_version):
    with pytest.raises(RuntimeError, match='Failed to find version for test-snapd-public'):
        assert await get_version("test", {
            "source": "snapcraft",
            "snap": "test-snapd-public",
            "channel": "non-existent-channel",
        })
