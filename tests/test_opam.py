# MIT licensed
# Copyright (c) 2024 Daniel Peukert <daniel@peukert.cc>, et al.

import pytest
pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]

async def test_opam_official(get_version):
    assert await get_version("test", {
        "source": "opam",
        "pkg": "omigrate",
    }) == "0.3.2"

async def test_opam_coq(get_version):
    assert await get_version("test", {
        "source": "opam",
        "repo": "https://coq.inria.fr/opam/released",
        "pkg": "coq-abp",
    }) == "8.10.0"

async def test_opam_coq_trailing_slash(get_version):
    assert await get_version("test", {
        "source": "opam",
        "repo": "https://coq.inria.fr/opam/released/",
        "pkg": "coq-abp",
    }) == "8.10.0"
