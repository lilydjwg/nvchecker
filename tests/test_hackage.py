from tests.helper import ExternalVersionTestCase


class HackageTest(ExternalVersionTestCase):
    def test_hackage(self):
        self.assertEqual(self.sync_get_version("sessions", {"hackage": None}), "2008.7.18")
