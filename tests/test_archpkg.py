# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import os

import pytest

from tests.helper import ExternalVersionTestCase

@pytest.mark.skipif("TRAVIS" in os.environ,
                    reason="Travis-CI has issues connecting to the Arch website")
class ArchPKGTest(ExternalVersionTestCase):
    def test_archpkg(self):
        self.assertEqual(self.sync_get_version("ipw2100-fw", {"archpkg": None}), "1.3-8")

    def test_archpkg_strip_release(self):
        self.assertEqual(self.sync_get_version("ipw2100-fw", {"archpkg": None, "strip-release": 1}), "1.3")
