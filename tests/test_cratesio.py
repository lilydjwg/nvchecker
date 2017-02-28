# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class CratesIOTest(ExternalVersionTestCase):
    def test_npm(self):
        self.assertEqual(
            self.sync_get_version("example", {"cratesio": None}),
            "0.1.0")
