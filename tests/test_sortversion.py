import pytest

from nvchecker.sortversion import parse_version, vercmp, vercmp_available

def test_parse_version():
  assert parse_version("v6.0") < parse_version("6.1")
  assert parse_version("v6.0") > parse_version("v6.1-stable")

@pytest.mark.skipif(not vercmp_available,
                    reason="needs pyalpm")
def test_vercmp():
  assert vercmp("v6.0") < vercmp("v6.1-stable")
