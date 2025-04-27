from anime_data_pipeline.defs.assets import *

import json

from unittest import mock


TEST_RAW_ANILIST_VALID = {
    "data": {
        "MediaListCollection": {
            "lists": [
                {
                    "name": "test_list",
                    "entries": [{"id": 1, "title": {"english": "test_title"}}],
                    "status": "test_status",
                }
            ]
        },
        "User": {
            "id": 1,
            "name": "test_user",
        },
    }
}

TEST_RAW_ANILIST_INVALID = {"data": {}}


@mock.patch("anime_data_pipeline.defs.resources.AniListAPIResource")
def test_raw_anilist_valid(mocked_anilist_api) -> None:
    mocked_anilist_api.query.return_value = TEST_RAW_ANILIST_VALID

    actual = raw_anilist(anilist_api=mocked_anilist_api)
    validated = raw_anilist_validate_check(actual.value)
    expected = mocked_anilist_api.query.return_value

    assert actual.value == expected
    assert validated.passed == True
    assert validated.metadata["size"].value == len(json.dumps(TEST_RAW_ANILIST_VALID))
    mocked_anilist_api.query.assert_called_once_with("anilist.graphql")


@mock.patch("anime_data_pipeline.defs.resources.AniListAPIResource")
def test_raw_anilist_invalid(mocked_anilist_api) -> None:
    mocked_anilist_api.query.return_value = TEST_RAW_ANILIST_INVALID

    actual = raw_anilist(anilist_api=mocked_anilist_api)
    validated = raw_anilist_validate_check(actual.value)
    expected = mocked_anilist_api.query.return_value

    assert actual.value == expected
    assert validated.passed == False
    assert validated.metadata["error"].value == "raw_anilist validation failed"
    mocked_anilist_api.query.assert_called_once_with("anilist.graphql")
