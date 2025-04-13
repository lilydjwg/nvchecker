# MIT licensed
# Copyright (c) 2025 Dani Rodríguez <dani@danirod.es>, et al.

import pytest

pytestmark = [pytest.mark.asyncio, pytest.mark.needs_net]


async def test_maven(get_version):
    # this package has been moved to a new name, so no new
    # versions should ever be published under this name
    assert (
        await get_version(
            "javax-persistence-api",
            {
                "source": "maven",
                "group": "javax.persistence",
                "artifact": "javax.persistence-api",
            },
        )
        == "2.2"
    )


async def test_maven_custom_repo(get_version):
    # this package has also been phased out in favour of another
    # so the version number should not bump unexpectedly
    assert (
        await get_version(
            "play-services",
            {
                "source": "maven",
                "repo": "https://maven.google.com",
                "group": "com.google.android.gms",
                "artifact": "play-services",
            },
        )
        == "12.0.1"
    )


async def test_maven_non_existing_group(get_version):
    with pytest.raises(
        RuntimeError, match="Failed to fetch metadata for javax:not-exists"
    ):
        assert await get_version(
            "persistence",
            {
                "source": "maven",
                "group": "javax",
                "artifact": "not-exists",
            },
        )


async def test_maven_cannot_find_release(get_version):
    # not exactly the way to pass parameters, but when concatted, it returns
    # an XML document without versioning info, so it allows to test decode
    # errors -> https://repo1.maven.org/maven2/org/apache/maven-metadata.xml
    with pytest.raises(RuntimeError, match="Failed to get version for org:apache"):
        assert await get_version(
            "apache",
            {
                "source": "maven",
                "group": "org",
                "artifact": "apache",
            },
        )
