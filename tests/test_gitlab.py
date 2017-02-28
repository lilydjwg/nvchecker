# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os
import pytest
from tests.helper import ExternalVersionTestCase


@pytest.mark.skipif("NVCHECKER_GITLAB_TOKEN_GITLAB_COM" not in os.environ,
                    reason="requires NVCHECKER_GITLAB_TOKEN_GITLAB_COM")
class GitLabTest(ExternalVersionTestCase):
    def test_gitlab(self):
        ver = self.sync_get_version("example",
                                    {"gitlab": "gitlab-org/gitlab-test"})
        self.assertEqual(len(ver), 8)
        self.assertTrue(ver.isdigit())

    def test_gitlab_max_tag(self):
        self.assertEqual(self.sync_get_version("example", {"gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1}), "v1.1.0")

    def test_gitlab_max_tag_with_ignored_tags(self):
        self.assertEqual(self.sync_get_version("example", {"gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1, "ignored_tags": "v1.1.0"}), "v1.0.0")
