# MIT licensed
# Copyright (c) 2023 Pekka Ristola <pekkarr [at] protonmail [dot] com>, et al.

import pathlib
import shutil
import subprocess
import tempfile

import pytest

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.skipif(shutil.which('pacman') is None, reason='requires pacman command'),
  pytest.mark.skipif(shutil.which('fakeroot') is None, reason='requires fakeroot command'),
]

global temp_dir, db_path


def setup_module(module):
  global temp_dir, db_path

  temp_dir = tempfile.TemporaryDirectory()
  temp_path = pathlib.Path(temp_dir.name)
  db_path = temp_path / 'test-db'

  db_path.mkdir(exist_ok=True)

  cmd = ['fakeroot', 'pacman', '-Fy', '--dbpath', db_path, '--disable-sandbox-filesystem']
  subprocess.check_call(cmd)


def teardown_module(module):
  temp_dir.cleanup()


async def test_alpmfiles(get_version):
  assert await get_version('test', {
    'source': 'alpmfiles',
    'pkgname': 'libuv',
    'filename': 'usr/lib/libuv\\.so\\.([^.]+)',
    'dbpath': db_path,
  }) == '1'

async def test_alpmfiles_strip(get_version):
  assert await get_version('test', {
    'source': 'alpmfiles',
    'pkgname': 'glibc',
    'repo': 'core',
    'filename': 'libc\\.so\\.[^.]+',
    'strip_dir': True,
    'dbpath': db_path,
  }) == 'libc.so.6'
