import pytest

from nvchecker.sortversion import (
  parse_version,
  vercmp, vercmp_available,
  AwesomeVersion, awesomeversion_available,
  portage_vercmp, portage_available,
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

@pytest.mark.skipif(not portage_available,
                    reason="needs portage")
def test_portage_vercmp():
  assert portage_vercmp("1.0") < portage_vercmp("1.1")
  assert portage_vercmp("1.0") < portage_vercmp("1.0-r1")
  assert portage_vercmp("1.0") < portage_vercmp("1.0_p1")
  assert [
    "1.0_alpha",
    "1.0_beta",
    "1.0_pre",
    "1.0_rc",
    "1.0",
    "1.0_p1",
  ] == sorted([
    "1.0_p1",
    "1.0",
    "1.0_rc",
    "1.0_pre",
    "1.0_beta",
    "1.0_alpha",
  ], key=portage_vercmp)
  assert [
    "1.0.0_alpha_pre",
    "1.0.0_alpha_rc1",
    "1.0.0_beta_pre",
    "1.0.0_beta_p1",
  ] == sorted([
    "1.0.0_beta_p1",
    "1.0.0_beta_pre",
    "1.0.0_alpha_rc1",
    "1.0.0_alpha_pre",
  ], key=portage_vercmp)
