# MIT licensed
# Copyright (c) 2020 DDoSolitary <DDoSolitary@gmail.com>, et al.

from nvchecker.api import GetVersionError
from pyalpm import Handle


async def open_db(info):
  dbpath, repo = info
  handle = Handle('/', dbpath)
  db = handle.register_syncdb(repo, 0)
  return (handle, db)


async def get_version(name, conf, *, cache, **kwargs):
  pkgname = conf.get('alpm', name)
  dbpath = conf.get('dbpath', '/var/lib/pacman')
  repo = conf.get('repo')
  strip_release = conf.get('strip_release', False)
  provided = conf.get('provided')
  db = (await cache.get((dbpath, repo), open_db))[1]
  pkg = db.get_pkg(pkgname)
  if pkg is None:
    raise GetVersionError('package not found in the ALPM database')
  if provided is None:
    version = pkg.version
  else:
    provides = dict(x.split('=', 1) for x in pkg.provides if '=' in x)
    version = provides.get(provided)
    if version is None:
      raise GetVersionError('provides element not found')
  if strip_release:
    version = version.split('-', 1)[0]
  return version
