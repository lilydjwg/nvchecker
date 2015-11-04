from nvchecker.get_version import get_version
import tornado.testing


class ExternalVersionTestCase(tornado.testing.AsyncTestCase):
    def sync_get_version(self, name, config):
        def get_version_callback(name, version):
            self.stop(version)

        get_version(name, config, get_version_callback)
        return self.wait()
