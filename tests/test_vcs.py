# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import shutil
import pytest
pytestmark = pytest.mark.asyncio


@pytest.mark.skipif(shutil.which("git") is None,
                    reason="requires git command")
async def test_git(get_version):
    assert await get_version("example", {
        "source": "vcs",
        "vcs": "git+https://github.com/harry-sanabria/ReleaseTestRepo.git",
    }) == "1.1.2b3cdf6134b07ae6ac77f11b586dc1ae6d1521db"

@pytest.mark.skipif(shutil.which("hg") is None,
                    reason="requires hg command")
async def test_mercurial(get_version):
    assert await get_version("example", {
        "source": "vcs",
        "vcs": "hg+https://bitbucket.org/pil0t/testrepo",
    }) == "1.1.84679e29c7d9"

@pytest.mark.skipif(shutil.which("git") is None,
                    reason="requires git command")
async def test_git_max_tag(get_version):
    assert await get_version("example", {
        "source": "vcs",
        "vcs": "git+https://github.com/harry-sanabria/ReleaseTestRepo.git",
        "use_max_tag": 1,
    }) == "second_release"

@pytest.mark.skipif(shutil.which("git") is None,
                    reason="requires git command")
async def test_git_max_tag_with_ignored(get_version):
    assert await get_version("example", {
        "source": "vcs",
        "vcs": "git+https://github.com/harry-sanabria/ReleaseTestRepo.git",
        "use_max_tag": 1,
        "ignored": "second_release release3",
    }) == "first_release"
