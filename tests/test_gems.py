# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class RubyGemsTest(ExternalVersionTestCase):
    def test_gems(self):
        self.assertEqual(self.sync_get_version("example", {"gems": None}), "1.0.2")
