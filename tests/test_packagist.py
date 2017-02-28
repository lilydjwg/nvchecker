# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class PackagistTest(ExternalVersionTestCase):
    def test_packagist(self):
        self.assertEqual(self.sync_get_version("butterfly/example-web-application", {"packagist": None}), "1.2.0")
