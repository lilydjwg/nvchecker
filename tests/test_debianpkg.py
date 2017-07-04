# MIT licensed
# Copyright (c) 2017 Felix Yan <felixonmars@archlinux.org>, et al.

import os

from tests.helper import ExternalVersionTestCase

class DebianPKGTest(ExternalVersionTestCase):
    def test_debianpkg(self):
        self.assertEqual(self.sync_get_version("sigrok-firmware-fx2lafw", {"debianpkg": None}), "0.1.3-1")

    def test_debianpkg_strip_release(self):
        self.assertEqual(self.sync_get_version("sigrok-firmware-fx2lafw", {"debianpkg": None, "strip-release": 1}), "0.1.3")

    def test_debianpkg_suite(self):
        self.assertEqual(self.sync_get_version("sigrok-firmware-fx2lafw", {"debianpkg": None, "suite": "jessie"}), "0.1.2-1")
