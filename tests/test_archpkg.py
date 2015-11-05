from tests.helper import ExternalVersionTestCase


class ArchPKGTest(ExternalVersionTestCase):
    def test_archpkg(self):
        self.assertEqual(self.sync_get_version("ipw2100-fw", {"archpkg": None}), "1.3-7")

    def test_archpkg_strip_release(self):
        self.assertEqual(self.sync_get_version("ipw2100-fw", {"archpkg": None, "strip-release": 1}), "1.3")
