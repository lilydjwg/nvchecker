# MIT licensed
# Copyright (c) 2025 Dani Rodríguez <dani@danirod.es>, et al.

from nvchecker.api import (
    Entry,
    KeyManager,
    AsyncCache,
    VersionResult,
    GetVersionError,
    HTTPError,
    session,
)
import pathlib
from xml.etree import ElementTree


MAVEN_CENTRAL = "https://repo1.maven.org/maven2"


async def get_version(
    name: str,
    conf: Entry,
    *,
    cache: AsyncCache,
    keymanager: KeyManager,
    **kwargs,
) -> VersionResult:
    # get project coordinates
    group_id, artifact_id = conf.get("group"), conf.get("artifact")
    if not group_id:
        raise GetVersionError("Group identifier is not given")
    if not artifact_id:
        raise GetVersionError("Artifact identifier is not given")
    group_id = group_id.replace(".", "/")

    # build the URL according to the transformation rules
    # -> https://maven.apache.org/repositories/layout.html
    repo = conf.get("repo", MAVEN_CENTRAL)
    repo_root = pathlib.PurePosixPath(repo)
    artifact_path = repo_root / group_id / artifact_id / "maven-metadata.xml"

    try:
        version = await cache.get(str(artifact_path), extract_metadata)
        if version is None:
            raise GetVersionError(f"Failed to get version for {group_id}:{artifact_id}")
        return version
    except HTTPError:
        raise GetVersionError(f"Failed to fetch metadata for {group_id}:{artifact_id}")


async def extract_metadata(url):
    metadata = await session.get(url)
    root = ElementTree.fromstring(metadata.body)
    release = root.find("./versioning/release")
    if release is not None:
        return release.text
