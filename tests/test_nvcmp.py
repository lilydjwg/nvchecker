import json
import logging
import sys

import pytest
import structlog

from nvchecker import core, sortversion

def write(tmp_path, conf, old, new):
  (tmp_path / 'c.toml').write_text(
    '[__config__]\noldver="old.json"\nnewver="new.json"\n' + conf)
  (tmp_path / 'old.json').write_text(old)
  (tmp_path / 'new.json').write_text(new)
  return str(tmp_path / 'c.toml')

@pytest.fixture
def run(tmp_path, monkeypatch, capsys):
  # process_common_arguments adds a root log handler per call, and structlog's
  # logger writes to stdout, where nvcmp -j puts its JSON.
  monkeypatch.setattr(core, 'process_common_arguments', lambda args: False)
  saved = structlog.get_config()
  structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL))

  def go(conf, old, new, *argv):
    path = write(tmp_path, conf, old, new)
    monkeypatch.setattr(sys, 'argv', ['nvcmp', '-c', path, *argv])
    from nvchecker.tools import cmp
    cmp()
    return capsys.readouterr().out
  yield go

  structlog.configure(**saved)

def test_per_entry_key_beats_sort(run):
  # these two hashes are ordered backwards by parse_version; swap them and the
  # test passes without the fix
  out = run(
    '[a]\nsource="manual"\nmanual="1"\nsort_version_key="none"\n'
    '[b]\nsource="manual"\nmanual="1"\n',
    '{"version":2,"data":{"a":{"version":"094fdb"},"b":{"version":"2.0"}}}',
    '{"version":2,"data":{"a":{"version":"decd9b"},"b":{"version":"1.0"}}}',
    '-n', '-j', '-q')
  assert json.loads(out) == ['a']

def test_sort_none_applies_without_per_entry_key(run):
  out = run(
    '[a]\nsource="manual"\nmanual="1"\n',
    '{"version":2,"data":{"a":{"version":"2.0"}}}',
    '{"version":2,"data":{"a":{"version":"1.0"}}}',
    '-s', 'none', '-j')
  assert json.loads(out)[0]['delta'] == 'new'

def test_unknown_key_exits(run):
  with pytest.raises(SystemExit) as e:
    run('[a]\nsource="manual"\nmanual="1"\nsort_version_key="bogus"\n',
        '{"version":2,"data":{"a":{"version":"1.0"}}}',
        '{"version":2,"data":{"a":{"version":"2.0"}}}')
  assert e.value.code == 2

def test_unavailable_comparator_exits(run, monkeypatch):
  # an absent library leaves a stub in the dict that raises when called
  def stub(v):
    raise NotImplementedError('stub')
  monkeypatch.setitem(sortversion.sort_version_keys, 'awesomeversion', stub)
  with pytest.raises(SystemExit) as e:
    run('[a]\nsource="manual"\nmanual="1"\nsort_version_key="awesomeversion"\n',
        '{"version":2,"data":{"a":{"version":"1.0"}}}',
        '{"version":2,"data":{"a":{"version":"2.0"}}}')
  assert e.value.code == 2
