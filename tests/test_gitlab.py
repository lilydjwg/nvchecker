import os
import pytest
from tests.helper import ExternalVersionTestCase


@pytest.mark.skipif("NVCHECKER_GITLAB_TOKEN_GITLAB_COM" not in os.environ,
                    reason="requires NVCHECKER_GITLAB_TOKEN_GITLAB_COM")
class GitLabTest(ExternalVersionTestCase):
    def test_gitlab(self):
        self.assertEqual(self.sync_get_version("example", {"gitlab": "gitlab-org/gitlab-test"}), "20150825")

    def test_gitlab_max_tag(self):
        self.assertEqual(self.sync_get_version("example", {"gitlab": "gitlab-org/gitlab-test", "use_max_tag": 1}), "v1.1.0")
