from nvchecker.get_version import get_version
import tornado.testing


class ExternalVersionTestCase(tornado.testing.AsyncTestCase):
    def sync_get_version(self, name, config):
        result = {}

        def get_version_callback(name, version):
            result["version"] = version
            self.stop()

        get_version(name, config, get_version_callback)
        self.wait()

        return result["version"]
