from tests.helper import ExternalVersionTestCase


class GitCafeTest(ExternalVersionTestCase):
    def test_gitcafe(self):
        self.assertEqual(self.sync_get_version("example", {"gitcafe": "test/test"}), "20120201")
