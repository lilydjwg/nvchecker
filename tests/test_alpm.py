# MIT licensed
# Copyright (c) 2020 DDoSolitary <DDoSolitary@gmail.com>, et al.

import pathlib
import shutil
import subprocess
import tempfile

import pytest

pytestmark = [
  pytest.mark.asyncio,
  pytest.mark.skipif(shutil.which('makepkg') is None, reason='requires makepkg command'),
  pytest.mark.skipif(shutil.which('repo-add') is None, reason='requires repo-add command')
]

global temp_dir, db_path


def setup_module(module):
  global temp_dir, db_path
  temp_dir = tempfile.TemporaryDirectory()
  temp_path = pathlib.Path(temp_dir.name)
  pkg_path = temp_path / 'test-pkg'
  pkg_path.mkdir()
  with (pkg_path / 'PKGBUILD').open('w') as f:
    f.write(
      'pkgname=test-pkg\n'
      'pkgver=1.2.3\n'
      'pkgrel=4\n'
      'arch=(any)\n'
      'provides=("test-provides=5.6-7" "test-provides-unversioned")\n'
    )
  subprocess.check_call(['makepkg', '--nosign'], cwd=pkg_path)
  pkg_file = subprocess.check_output(['makepkg', '--packagelist'], cwd=pkg_path, text=True).strip()
  db_path = pkg_path / 'test-db'
  db_path.mkdir()
  repo_path = db_path / 'sync'
  repo_path.mkdir()
  subprocess.check_call([
    'repo-add',
    repo_path / 'test-repo.db.tar.gz',
    pkg_path / pkg_file
  ])


def teardown_module(module):
  temp_dir.cleanup()


async def test_alpm(get_version):
  assert await get_version('test-pkg', {
    'source': 'alpm',
    'dbpath': str(db_path),
    'repo': 'test-repo'
  }) == '1.2.3-4'


async def test_alpm_strip(get_version):
  assert await get_version('test-pkg', {
    'source': 'alpm',
    'dbpath': str(db_path),
    'repo': 'test-repo',
    'strip_release': True
  }) == '1.2.3'


async def test_alpm_provided(get_version):
  assert await get_version('test-pkg', {
    'source': 'alpm',
    'dbpath': str(db_path),
    'repo': 'test-repo',
    'provided': 'test-provides'
  }) == '5.6-7'


async def test_alpm_provided_strip(get_version):
  assert await get_version('test-pkg', {
    'source': 'alpm',
    'dbpath': str(db_path),
    'repo': 'test-repo',
    'provided': 'test-provides',
    'strip_release': True
  }) == '5.6'


async def test_alpm_missing_repo(get_version):
  with pytest.raises(RuntimeError):
    await get_version('test-pkg', {
      'source': 'alpm',
      'dbpath': str(db_path),
      'repo': 'wrong-repo'
    })


async def test_alpm_missing_pkg(get_version):
  with pytest.raises(RuntimeError):
    await get_version('wrong-pkg', {
      'source': 'alpm',
      'dbpath': str(db_path),
      'repo': 'test-repo'
    })


async def test_alpm_missing_provides(get_version):
  with pytest.raises(RuntimeError):
    await get_version('test-pkg', {
      'source': 'alpm',
      'dbpath': str(db_path),
      'repo': 'test-repo',
      'provided': 'wrong-provides'
    })
