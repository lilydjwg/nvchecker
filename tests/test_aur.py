# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class AURTest(ExternalVersionTestCase):
    def test_aur(self):
        self.assertEqual(self.sync_get_version("asciidoc-fake", {"aur": None}), "1.0-1")

    def test_aur_strip_release(self):
        self.assertEqual(self.sync_get_version("asciidoc-fake", {"aur": None, "strip-release": 1}), "1.0")
