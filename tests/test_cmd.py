from tornado.ioloop import IOLoop
from tests.helper import ExternalVersionTestCase


class CMDTest(ExternalVersionTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()

    def test_cmd(self):
        self.assertEqual(self.sync_get_version("example", {"cmd": "echo Meow"}), "Meow")
