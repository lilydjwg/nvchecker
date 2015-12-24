from flaky import flaky
from tests.helper import ExternalVersionTestCase


class GitCafeTest(ExternalVersionTestCase):
    @flaky(max_runs=7)
    def test_gitcafe(self):
        self.assertEqual(self.sync_get_version("example", {"gitcafe": "test/test"}), "20120201")
