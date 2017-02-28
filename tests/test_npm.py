# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class NPMTest(ExternalVersionTestCase):
    def test_npm(self):
        self.assertEqual(self.sync_get_version("example", {"npm": None}), "0.0.0")
