# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import pytest
from tests.helper import ExternalVersionTestCase


@pytest.mark.skipif("NVCHECKER_GITHUB_TOKEN" not in os.environ,
                    reason="requires NVCHECKER_GITHUB_TOKEN, or it fails too much")
class GitHubTest(ExternalVersionTestCase):
    def test_github(self):
        self.assertEqual(self.sync_get_version("example", {"github": "harry-sanabria/ReleaseTestRepo"}), "20140122.012101")

    def test_github_latest_release(self):
        self.assertEqual(self.sync_get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_latest_release": 1}), "release3")

    def test_github_max_tag(self):
        self.assertEqual(self.sync_get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_max_tag": 1}), "second_release")

    def test_github_max_tag_with_ignored_tags(self):
        self.assertEqual(self.sync_get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_max_tag": 1, "ignored_tags": "second_release release3"}), "first_release")
