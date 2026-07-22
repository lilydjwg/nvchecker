import json

from nvchecker.core import _process_result, json_encode
from nvchecker.util import RawResult, RichResult


def test_timestamps_survive_list_selection():
    result = _process_result(
        RawResult(
            "test",
            [
                RichResult(
                    version="1.0",
                    creation_time="2026-07-20T12:00:00Z",
                    revision_creation_time="2026-07-19T10:00:00Z",
                ),
                RichResult(
                    version="2.0",
                    creation_time="2026-07-22T12:00:00Z",
                    revision_creation_time="2026-07-21T10:00:00Z",
                ),
            ],
            {},
        )
    )

    assert result == RichResult(
        version="2.0",
        creation_time="2026-07-22T12:00:00Z",
        revision_creation_time="2026-07-21T10:00:00Z",
    )


def test_timestamps_serialize_when_present():
    result = json.loads(
        json.dumps(
            RichResult(
                version="1.2.3",
                creation_time="2026-07-22T12:00:00Z",
                revision_creation_time="2026-07-21T10:00:00Z",
            ),
            default=json_encode,
        )
    )

    assert result == {
        "version": "1.2.3",
        "creation_time": "2026-07-22T12:00:00Z",
        "revision_creation_time": "2026-07-21T10:00:00Z",
    }


def test_creation_time_omitted_when_none():
    result = json.loads(
        json.dumps(
            RichResult(
                version="1.2.3",
                revision_creation_time="2026-07-21T10:00:00Z",
            ),
            default=json_encode,
        )
    )

    assert result == {
        "version": "1.2.3",
        "revision_creation_time": "2026-07-21T10:00:00Z",
    }


def test_revision_creation_time_omitted_when_none():
    result = json.loads(
        json.dumps(
            RichResult(
                version="1.2.3",
                creation_time="2026-07-22T12:00:00Z",
            ),
            default=json_encode,
        )
    )

    assert result == {
        "version": "1.2.3",
        "creation_time": "2026-07-22T12:00:00Z",
    }


def test_timestamps_omitted_when_none():
    result = json.loads(
        json.dumps(
            RichResult(version="1.2.3"),
            default=json_encode,
        )
    )

    assert result == {
        "version": "1.2.3",
    }


def test_rich_result_metadata_survives_normalization():
    result = _process_result(
        RawResult(
            "test",
            RichResult(
                version="v1.2.3",
                url="https://example.com/release",
                gitref="refs/tags/v1.2.3",
                revision="abcdef",
                creation_time="2026-07-22T12:00:00Z",
                revision_creation_time="2026-07-21T10:00:00Z",
            ),
            {"prefix": "v"},
        )
    )

    assert result == RichResult(
        version="1.2.3",
        url="https://example.com/release",
        gitref="refs/tags/v1.2.3",
        revision="abcdef",
        creation_time="2026-07-22T12:00:00Z",
        revision_creation_time="2026-07-21T10:00:00Z",
    )
