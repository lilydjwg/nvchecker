# MIT licensed
# Copyright (c) 2024 Daniel Peukert <daniel@peukert.cc>, et al.

import asyncio
from io import BytesIO
import tarfile
from typing import List

from nvchecker.api import (
  session, VersionResult,
  Entry, AsyncCache,
  KeyManager, RichResult
)

OPAM_REPO_INDEX_URL = "%s/index.tar.gz"
OPAM_VERSION_PATH_PREFIX = "packages/%s/%s."
OPAM_VERSION_PATH_SUFFIX = "/opam"

OPAM_DEFAULT_REPO = 'https://opam.ocaml.org'
OPAM_DEFAULT_REPO_VERSION_URL = "%s/packages/%s/%s.%s"

def _decompress_and_list_files(data: bytes) -> List[str]:
  # Convert the bytes to a file object and get a list of files
  with tarfile.open(mode='r', fileobj=BytesIO(data)) as archive:
    return archive.getnames()

async def get_files(url: str) -> List[str]:
  # Download the file and get its contents
  res = await session.get(url)
  data = res.body

  # Get the file list of the archive
  loop = asyncio.get_running_loop()
  return await loop.run_in_executor(None, _decompress_and_list_files, data)

async def get_package_versions(files: List[str], pkg: str) -> List[str]:
  # Prepare the filename prefix based on the package name
  prefix = OPAM_VERSION_PATH_PREFIX % (pkg , pkg)

  # Only keep opam files that are relevant to the package we're working with
  filtered_files = []

  for filename in files:
    if filename.startswith(prefix) and filename.endswith(OPAM_VERSION_PATH_SUFFIX):
      filtered_files.append(filename[len(prefix):-1*len(OPAM_VERSION_PATH_SUFFIX)])

  return filtered_files

async def get_version(
  name: str, conf: Entry, *,
  cache: AsyncCache, keymanager: KeyManager,
  **kwargs,
):
  pkg = conf.get('pkg', name)
  repo = conf.get('repo', OPAM_DEFAULT_REPO).rstrip('/')

  # Get the list of files in the repo index (see https://opam.ocaml.org/doc/Manual.html#Repositories for repo structure)
  files = await cache.get(OPAM_REPO_INDEX_URL % repo, get_files) # type: ignore

  # Parse the version strings from the file names
  raw_versions = await get_package_versions(files, pkg)

  # Convert the version strings into RichResults
  versions = []
  for version in raw_versions:
    versions.append(RichResult(
      version = version,
      # There is no standardised URL scheme, so we only return an URL for the default registry
      url = OPAM_DEFAULT_REPO_VERSION_URL % (repo, pkg, pkg, version) if repo == OPAM_DEFAULT_REPO else None,
    ))
  return versions
