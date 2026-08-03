# MIT licensed
# Copyright (c) 2026 lilydjwg <lilydjwg@gmail.com>, et al.

from unittest.mock import patch

from nvchecker.core import check_version_update
from nvchecker.util import RichResult


def test_updated_event_contains_rich_result():
    with patch("nvchecker.core.logger.info") as info:
        check_version_update(
            oldvers={},
            name="example",
            r=RichResult(
                version="1.2.3",
                revision="abc123",
                url="https://example.invalid",
                gitref="refs/tags/v1.2.3",
            ),
            verbose=False,
        )

    info.assert_called_once()

    _, kwargs = info.call_args

    assert kwargs["name"] == "example"
    assert kwargs["version"] == "1.2.3"
    assert kwargs["revision"] == "abc123"
    assert kwargs["old_version"] is None
    assert kwargs["url"] == "https://example.invalid"

    assert kwargs["rich_result"] == {
        "version": "1.2.3",
        "revision": "abc123",
        "url": "https://example.invalid",
        "gitref": "refs/tags/v1.2.3",
    }


def test_updated_event_omits_none_rich_result_fields():
    with patch("nvchecker.core.logger.info") as info:
        check_version_update(
            oldvers={},
            name="example",
            r=RichResult(version="1.2.3"),
            verbose=False,
        )

    info.assert_called_once()

    _, kwargs = info.call_args

    assert kwargs["rich_result"] == {
        "version": "1.2.3",
    }
