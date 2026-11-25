# MIT licensed
# Copyright (c) 2026 lilydjwg <lilydjwg@gmail.com>, et al.

from __future__ import annotations

import asyncio
import base64
import subprocess
import sys
from unittest.mock import patch

import pytest

from nvchecker import __main__ as main
from nvchecker import core
from nvchecker.util import Entries, RawResult, ResultData

httpbin_available = True
try:
  import pytest_httpbin
  assert pytest_httpbin  # for pyflakes
except ImportError:
  httpbin_available = False

pytestmark = [
  pytest.mark.skipif(not httpbin_available, reason="needs pytest_httpbin"),
]


def base64_encode(s: str) -> str:
  return base64.b64encode(s.encode('utf-8')).decode('ascii')


async def run_with_log_prefix(
  entries: Entries,
  log_failures_prefix: str,
  httplib: str | None = None,
) -> tuple[ResultData, bool]:
  task_sem = asyncio.Semaphore(20)
  result_q: asyncio.Queue[RawResult] = asyncio.Queue()
  keymanager = core.KeyManager(None)
  dispatcher = core.setup_httpclient(httplib=httplib)
  entry_waiter = core.EntryWaiter()
  entry_responses: dict[str, list[bytes]] = {}
  futures = dispatcher.dispatch(
    entries, task_sem, result_q,
    keymanager, entry_waiter, 1, {},
    entry_responses=entry_responses,
  )
  oldvers: ResultData = {}
  result_coro = core.process_result(
    oldvers, result_q, entry_waiter,
    log_failures_prefix=log_failures_prefix,
    entry_responses=entry_responses,
  )
  runner_coro = core.run_tasks(futures)
  with patch("nvchecker.core.logger.error"):
    return await main.run(result_coro, runner_coro)


@pytest.mark.asyncio
async def test_log_failures_on_regex_mismatch(httpbin, tmp_path):
  prefix = str(tmp_path / "nvfail-")
  payload = "unexpected response content"
  entries = {
    "ok-pkg": {
      "source": "regex",
      "url": httpbin.url + "/base64/" + base64_encode("version 1.2.3"),
      "regex": r"version ([0-9.]+)",
    },
    "fail-pkg": {
      "source": "regex",
      "url": httpbin.url + "/base64/" + base64_encode(payload),
      "regex": r"version ([0-9.]+)",
    },
  }

  results, has_failures = await run_with_log_prefix(entries, prefix)

  assert has_failures is True
  assert "ok-pkg" in results
  assert "fail-pkg" not in results
  assert not (tmp_path / "nvfail-ok-pkg.txt").exists()
  fail_file = tmp_path / "nvfail-fail-pkg.txt"
  assert fail_file.exists()
  assert fail_file.read_bytes() == payload.encode("utf-8")


@pytest.mark.asyncio
async def test_log_failures_shared_cache(httpbin, tmp_path):
  prefix = str(tmp_path / "nvfail-")
  payload = "version 2.0.0 only"
  url = httpbin.url + "/base64/" + base64_encode(payload)
  entries = {
    "cached-ok": {
      "source": "regex",
      "url": url,
      "regex": r"version ([0-9.]+)",
    },
    "cached-fail": {
      "source": "regex",
      "url": url,
      "regex": r"missing ([0-9.]+)",
    },
  }

  results, has_failures = await run_with_log_prefix(entries, prefix)

  assert has_failures is True
  assert "cached-ok" in results
  assert "cached-fail" not in results
  assert not (tmp_path / "nvfail-cached-ok.txt").exists()
  fail_file = tmp_path / "nvfail-cached-fail.txt"
  assert fail_file.exists()
  assert fail_file.read_bytes() == payload.encode("utf-8")


@pytest.mark.asyncio
async def test_log_failures_on_http_error(httpbin, tmp_path):
  from nvchecker.httpclient.base import HTTPError
  err = HTTPError(418, "I'M A TEAPOT", None, b"secret-response-body")
  assert "secret-response-body" not in repr(err)
  assert err.body == b"secret-response-body"

  prefix = str(tmp_path / "nvfail-")
  entries = {
    "teapot": {
      "source": "regex",
      "url": httpbin.url + "/status/418",
      "regex": r"version ([0-9.]+)",
    },
  }

  results, has_failures = await run_with_log_prefix(entries, prefix)

  assert has_failures is True
  assert results == {}
  fail_file = tmp_path / "nvfail-teapot.txt"
  assert fail_file.exists()
  assert b"teapot" in fail_file.read_bytes()


@pytest.mark.asyncio
async def test_log_failures_sanitizes_entry_name(httpbin, tmp_path):
  prefix = str(tmp_path / "nvfail-")
  payload = "body for slashed entry"
  entries = {
    "group/pkg": {
      "source": "regex",
      "url": httpbin.url + "/base64/" + base64_encode(payload),
      "regex": r"no-match",
    },
  }

  _, has_failures = await run_with_log_prefix(entries, prefix)

  assert has_failures is True
  fail_file = tmp_path / "nvfail-group_pkg.txt"
  assert fail_file.exists()
  assert fail_file.read_bytes() == payload.encode("utf-8")


@pytest.mark.asyncio
async def test_no_log_without_http_response(httpbin, tmp_path):
  prefix = str(tmp_path / "nvfail-")
  entries = {
    "bad-regex": {
      "source": "regex",
      "url": httpbin.url + "/get",
      "regex": r"[unclosed",
    },
  }

  _, has_failures = await run_with_log_prefix(entries, prefix)

  assert has_failures is True
  assert not (tmp_path / "nvfail-bad-regex.txt").exists()


def test_log_failures_cli(httpbin, tmp_path):
  payload = "cli failure body"
  conf = tmp_path / "nvchecker.toml"
  conf.write_text(
    f'''\
[ok-entry]
source = "regex"
url = "{httpbin.url}/base64/{base64_encode("version 3.1.4")}"
regex = "version ([0-9.]+)"

[fail-entry]
source = "regex"
url = "{httpbin.url}/base64/{base64_encode(payload)}"
regex = "version ([0-9.]+)"
''',
    encoding="utf-8",
  )
  prefix = str(tmp_path / "logs" / "nvfail-")

  proc = subprocess.run(
    [
      sys.executable, "-m", "nvchecker",
      "-c", str(conf),
      "--failures",
      "--log-failures-prefix", prefix,
    ],
    capture_output=True,
    text=True,
  )

  assert proc.returncode == 3
  assert not (tmp_path / "logs" / "nvfail-ok-entry.txt").exists()
  fail_file = tmp_path / "logs" / "nvfail-fail-entry.txt"
  assert fail_file.exists()
  assert fail_file.read_bytes() == payload.encode("utf-8")
