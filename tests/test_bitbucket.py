from tests.helper import ExternalVersionTestCase


class BitBucketTest(ExternalVersionTestCase):
    def test_bitbucket(self):
        self.assertEqual(self.sync_get_version("example", {"bitbucket": "prawee/git-tag"}), "20150303")

    def test_bitbucket_max_tag(self):
        self.assertEqual(self.sync_get_version("example", {"bitbucket": "prawee/git-tag", "use_max_tag": 1}), "1.7.0")
