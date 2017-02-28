# MIT licensed
# Copyright (c) 2013-2017 lilydjwg <lilydjwg@gmail.com>, et al.

import configparser
from tornado.ioloop import IOLoop
import tornado.testing
from nvchecker.get_version import get_version


class ExternalVersionTestCase(tornado.testing.AsyncTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()

    def sync_get_version(self, name, config):
        def get_version_callback(name, version):
            self.stop(version)

        if isinstance(config, dict):
            _config = configparser.ConfigParser(dict_type=dict, allow_no_value=True)
            _config.read_dict({name: config})
            config = _config[name]

        get_version(name, config, get_version_callback)
        return self.wait()
