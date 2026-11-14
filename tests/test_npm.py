# MIT licensed
# Copyright (c) 2013-2020 lilydjwg <lilydjwg@gmail.com>, et al.

import pytest

from nvchecker_source import npm

@pytest.mark.asyncio
@pytest.mark.needs_net
async def test_npm(get_version):
    assert await get_version("example", {
        "source": "npm",
    }) == "0.0.0"

def test_parse_dist_tags():
  data = b'{"name":"example","dist-tags":{"latest":"1.2.3","next":"2.0.0-rc.1"}}'
  assert npm.parse_dist_tags(data) == {
    "latest": "1.2.3",
    "next": "2.0.0-rc.1",
  }

def test_parse_dist_tags_truncated():
  data = b'{"name":"example","dist-tags":{"latest":"1.2.3","next":"2.0.'
  assert npm.parse_dist_tags(data) is None

def test_parse_dist_tags_missing():
  assert npm.parse_dist_tags(b'{"name":"example"}') is None

class FakeResponse:
  def __init__(self, body):
    self.body = body


class FakeSession:
  def __init__(self, bodies, calls):
    self._bodies = bodies
    self._calls = calls

  async def get(self, url, headers=None):
    self._calls.append(dict(headers or {}))
    index = min(len(self._calls) - 1, len(self._bodies) - 1)
    return FakeResponse(self._bodies[index])


def fake_session(monkeypatch, bodies):
  calls = []
  monkeypatch.setattr(npm, 'session', FakeSession(bodies, calls))
  return calls

@pytest.mark.asyncio
async def test_get_metadata_falls_back_to_full(monkeypatch):
  calls = fake_session(monkeypatch, [
    b'{"name":"example","dist-tags":{"latest":"1.2.',
    b'{"name":"example","dist-tags":{"latest":"1.2.3"}}',
  ])
  data = await npm.get_metadata("https://registry.example/example")
  assert npm.parse_dist_tags(data) == {"latest": "1.2.3"}
  assert len(calls) == 2
  assert "Range" in calls[0]
  assert "Range" not in calls[1]

@pytest.mark.asyncio
async def test_get_metadata_single_request_when_complete(monkeypatch):
  calls = fake_session(monkeypatch, [
    b'{"name":"example","dist-tags":{"latest":"1.2.3"}}',
  ])
  data = await npm.get_metadata("https://registry.example/example")
  assert npm.parse_dist_tags(data) == {"latest": "1.2.3"}
  assert len(calls) == 1

class FakeCache:
  async def get(self, key, getter):
    return await getter(key)

@pytest.mark.asyncio
async def test_get_version_raises_on_unparsable_dist_tags(monkeypatch):
  fake_session(monkeypatch, [b'{"name":"example"}'])
  with pytest.raises(ValueError, match="dist-tags"):
    await npm.get_version("example", {"npm": "example"}, cache=FakeCache())
