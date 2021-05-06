import pytest

from nvchecker.sortversion import sort_version_keys

def test_parse_version():
  parse_version = sort_version_keys("parse_version")
  assert parse_version("v6.0") < parse_version("6.1")
  assert parse_version("v6.0") > parse_version("v6.1-stable")

def test_packaging():
  packaging_version = sort_version_keys("packaging")
  assert packaging_version("v6.0") < packaging_version("6.1")
  assert packaging_version("v6.0") > packaging_version("v6.1-stable")

def test_vercmp():
  try:
    vercmp = sort_version_keys("vercmp")
  except ImportError:
    pytest.skip("needs pyalpm")
  assert vercmp("v6.0") < vercmp("v6.1-stable")
