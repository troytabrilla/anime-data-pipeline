from anime_data_pipeline.defs.assets import *

import json

from unittest import mock


TEST_RAW_ANILIST_VALID = {
    "data": {
        "MediaListCollection": {
            "lists": [
                {
                    "name": "test_list",
                    "entries": [
                        {
                            "id": 1,
                            "media": {
                                "id": 2,
                                "genres": ["test_genre"],
                                "description": "test_description",
                                "title": {
                                    "english": "test_title",
                                },
                                "status": "test_media_status",
                                "averageScore": 50,
                                "meanScore": 50,
                                "popularity": 1234,
                                "trending": 0,
                                "favourites": 3,
                                "episodes": 12,
                                "tags": [
                                    {
                                        "category": "test_tag_category",
                                        "description": "test_tag_description.",
                                        "name": "test_tag_name",
                                        "rank": 80,
                                    },
                                ],
                                "stats": {},
                                "rankings": [],
                            },
                            "progress": 1,
                            "score": 7,
                            "status": "test_entry_status",
                            "mediaId": 2,
                            "userId": 42,
                        }
                    ],
                    "status": "test_list_status",
                }
            ]
        },
        "User": {
            "id": 42,
            "name": "test_user",
        },
    }
}

TEST_RAW_ANILIST_INVALID = {
    "data": {"MediaListCollection": {"lists": []}},
}

TEST_FACT_ANIME_VALID = [
    {
        "id": 1,
        "user_id": 42,
        "media_id": 2,
        "average_score": 50,
        "mean_score": 50,
        "popularity": 1234,
        "trending": 0,
        "favourites": 3,
        "progress": 1,
        "episodes": 12,
        "score": 7,
        "watch_status": "test_entry_status",
        "started_at": None,
        "completed_at": None,
        "stats": {},
        "rankings": [],
    }
]

TEST_FACT_ANIME_INVALID = []


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


@mock.patch("dagster_duckdb_pandas.DuckDBPandasIOManager")
def test_fact_anime_valid(mocked_duckdb_io_manager) -> None:
    actual = fact_anime(TEST_RAW_ANILIST_VALID)
    validated = fact_anime_validate_check(actual)
    expected = pd.DataFrame.from_dict(TEST_FACT_ANIME_VALID)

    assert actual.equals(expected)
    assert validated.passed == True
    assert validated.metadata["count"].value == 1


@mock.patch("dagster_duckdb_pandas.DuckDBPandasIOManager")
def test_fact_anime_invalid(mocked_duckdb_io_manager) -> None:
    actual = fact_anime(TEST_RAW_ANILIST_INVALID)
    validated = fact_anime_validate_check(actual)
    expected = pd.DataFrame.from_dict(TEST_FACT_ANIME_INVALID)

    assert actual.equals(expected)
    assert validated.passed == False
    assert validated.metadata["count"].value == 0
    assert validated.metadata["error"].value == "no rows processed"
