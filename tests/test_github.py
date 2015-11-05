from tests.helper import ExternalVersionTestCase


class GitHubTest(ExternalVersionTestCase):
    def test_github(self):
        self.assertEqual(self.sync_get_version("example", {"github": "harry-sanabria/ReleaseTestRepo"}), "20140122")

    def test_github_latest_release(self):
        self.assertEqual(self.sync_get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_latest_release": 1}), "release3")

    def test_github_max_tag(self):
        self.assertEqual(self.sync_get_version("example", {"github": "harry-sanabria/ReleaseTestRepo", "use_max_tag": 1}), "second_release")
