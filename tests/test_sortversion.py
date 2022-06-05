import pytest

from nvchecker.sortversion import (
  parse_version,
  vercmp, vercmp_available,
  AwesomeVersion, awesomeversion_available,
)

def test_parse_version():
  assert parse_version("v6.0") < parse_version("6.1")
  assert parse_version("v6.0") > parse_version("v6.1-stable")

@pytest.mark.skipif(not vercmp_available,
                    reason="needs pyalpm")
def test_vercmp():
  assert vercmp("v6.0") < vercmp("v6.1-stable")

@pytest.mark.skipif(not awesomeversion_available,
                    reason="needs awesomeversion")
def test_awesomeversion():
  assert AwesomeVersion("v6.0") < AwesomeVersion("6.1")
  assert AwesomeVersion("v6.0") > AwesomeVersion("v6.0b0")

