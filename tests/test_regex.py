# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class RegexTest(ExternalVersionTestCase):
    def test_regex(self):
        self.assertEqual(self.sync_get_version("example", {
            "url": "https://httpbin.org/get",
            "regex": '"User-Agent": "(\w+)"',
            "user_agent": "Meow",
        }), "Meow")
