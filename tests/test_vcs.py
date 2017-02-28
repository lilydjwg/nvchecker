# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import shutil
import pytest
from tests.helper import ExternalVersionTestCase


class VCSTest(ExternalVersionTestCase):
    @pytest.mark.skipif(shutil.which("git") is None,
                        reason="requires git command")
    def test_git(self):
        os.path.exists("example") or os.mkdir("example")
        self.assertEqual(self.sync_get_version("example", {"vcs": "git+https://github.com/harry-sanabria/ReleaseTestRepo.git"}), "1.1.2b3cdf6134b07ae6ac77f11b586dc1ae6d1521db")

    @pytest.mark.skipif(shutil.which("hg") is None,
                        reason="requires hg command")
    def test_mercurial(self):
        os.path.exists("example") or os.mkdir("example")
        self.assertEqual(self.sync_get_version("example", {"vcs": "hg+https://bitbucket.org/pil0t/testrepo"}), "1.1.84679e29c7d9")

    @pytest.mark.skipif(shutil.which("git") is None,
                        reason="requires git command")
    def test_git_max_tag(self):
        os.path.exists("example") or os.mkdir("example")
        self.assertEqual(self.sync_get_version("example", {"vcs": "git+https://github.com/harry-sanabria/ReleaseTestRepo.git", "use_max_tag": 1}), "second_release")

    @pytest.mark.skipif(shutil.which("git") is None,
                        reason="requires git command")
    def test_git_max_tag_with_ignored_tags(self):
        os.path.exists("example") or os.mkdir("example")
        self.assertEqual(self.sync_get_version("example", {"vcs": "git+https://github.com/harry-sanabria/ReleaseTestRepo.git", "use_max_tag": 1, "ignored_tags": "second_release release3"}), "first_release")
