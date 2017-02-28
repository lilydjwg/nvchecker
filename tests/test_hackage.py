# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class HackageTest(ExternalVersionTestCase):
    def test_hackage(self):
        self.assertEqual(self.sync_get_version("sessions", {"hackage": None}), "2008.7.18")
