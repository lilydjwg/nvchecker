# MIT licensed
# Copyright (c) 2023 Pekka Ristola <pekkarr [at] protonmail [dot] com>, et al.

import shutil

import pytest

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.skipif(shutil.which('pacman') is None, reason='requires pacman command'),
]

async def test_alpmfiles(get_version):
  assert await get_version('test', {
    'source': 'alpmfiles',
    'pkgname': 'libuv',
    'filename': 'usr/lib/libuv\\.so\\.([^.]+)',
  }) == '1'

async def test_alpmfiles_strip(get_version):
  assert await get_version('test', {
    'source': 'alpmfiles',
    'pkgname': 'glibc',
    'repo': 'core',
    'filename': 'libc\\.so\\.[^.]+',
    'strip_dir': True,
    'dbpath': '/var/lib/pacman',
  }) == 'libc.so.6'
