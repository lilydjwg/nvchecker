# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

from tests.helper import ExternalVersionTestCase


class CMDTest(ExternalVersionTestCase):
    def test_cmd(self):
        self.assertEqual(self.sync_get_version("example", {"cmd": "echo Meow"}), "Meow")
