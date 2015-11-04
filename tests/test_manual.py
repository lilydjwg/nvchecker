from tests.helper import ExternalVersionTestCase


class ManualTest(ExternalVersionTestCase):
    def test_manual(self):
        self.assertEqual(self.sync_get_version("example", {"manual": "Meow"}), "Meow")
