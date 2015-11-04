from tests.helper import ExternalVersionTestCase


class CPANTest(ExternalVersionTestCase):
    def test_cpan(self):
        self.assertEqual(self.sync_get_version("POE-Component-Server-HTTPServer", {"cpan": None}), "0.9.2")
