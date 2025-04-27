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
                                    "native": "test_native",
                                    "romaji": "test_romaji",
                                },
                                "coverImage": {"extraLarge": "test_cover_image"},
                                "type": "test_type",
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
                                "format": "test_format",
                                "season": "test_season",
                                "seasonYear": 2025,
                                "synonyms": ["test_synonyms"],
                                "source": "test_source",
                                "bannerImage": "test_banner_image",
                                "siteUrl": "test_site_url",
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
            "avatar": {
                "large": "test_avatar",
            },
            "bannerImage": "test_user_banner_image",
            "siteUrl": "test_user_site_url",
            "statistics": {},
        },
    }
}
TEST_RAW_ANILIST_INVALID = {}

TEST_LISTS = TEST_RAW_ANILIST_VALID["data"]["MediaListCollection"]["lists"]
TEST_FACT_ANIME_VALID = [
    {
        "id": TEST_LISTS[0]["entries"][0]["id"],
        "user_id": TEST_LISTS[0]["entries"][0]["userId"],
        "media_id": TEST_LISTS[0]["entries"][0]["media"]["id"],
        "average_score": TEST_LISTS[0]["entries"][0]["media"]["averageScore"],
        "mean_score": TEST_LISTS[0]["entries"][0]["media"]["meanScore"],
        "popularity": TEST_LISTS[0]["entries"][0]["media"]["popularity"],
        "trending": TEST_LISTS[0]["entries"][0]["media"]["trending"],
        "favourites": TEST_LISTS[0]["entries"][0]["media"]["favourites"],
        "progress": TEST_LISTS[0]["entries"][0]["progress"],
        "episodes": TEST_LISTS[0]["entries"][0]["media"]["episodes"],
        "score": TEST_LISTS[0]["entries"][0]["score"],
        "watch_status": TEST_LISTS[0]["entries"][0]["status"],
        "started_at": None,
        "completed_at": None,
        "stats": {},
        "rankings": [],
    }
]
TEST_FACT_ANIME_INVALID = []

TEST_DIMENSION_MEDIA_VALID = [
    {
        "id": TEST_LISTS[0]["entries"][0]["media"]["id"],
        "genres": TEST_LISTS[0]["entries"][0]["media"]["genres"],
        "description": TEST_LISTS[0]["entries"][0]["media"]["description"],
        "cover_image": TEST_LISTS[0]["entries"][0]["media"]["coverImage"]["extraLarge"],
        "type": TEST_LISTS[0]["entries"][0]["media"]["type"],
        "tags": TEST_LISTS[0]["entries"][0]["media"]["tags"],
        "episodes": TEST_LISTS[0]["entries"][0]["media"]["episodes"],
        "format": TEST_LISTS[0]["entries"][0]["media"]["format"],
        "season": TEST_LISTS[0]["entries"][0]["media"]["season"],
        "season_year": TEST_LISTS[0]["entries"][0]["media"]["seasonYear"],
        "start_date": None,
        "end_date": None,
        "synonyms": TEST_LISTS[0]["entries"][0]["media"]["synonyms"],
        "title": TEST_LISTS[0]["entries"][0]["media"]["title"],
        "source": TEST_LISTS[0]["entries"][0]["media"]["source"],
        "banner_image": TEST_LISTS[0]["entries"][0]["media"]["bannerImage"],
        "site_url": TEST_LISTS[0]["entries"][0]["media"]["siteUrl"],
        "status": TEST_LISTS[0]["entries"][0]["media"]["status"],
    }
]
TEST_DIMENSION_MEDIA_INVALID = []

TEST_USER = TEST_RAW_ANILIST_VALID["data"]["User"]
TEST_DIMENSION_USER_VALID = [
    {
        "id": TEST_USER["id"],
        "name": TEST_USER["name"],
        "avatar": TEST_USER["avatar"]["large"],
        "banner_image": TEST_USER["bannerImage"],
        "site_url": TEST_USER["siteUrl"],
        "statistics": TEST_USER["statistics"],
    }
]
TEST_DIMENSION_USER_INVALID = []


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


@mock.patch("dagster_duckdb_pandas.DuckDBPandasIOManager")
def test_dimension_media_valid(mocked_duckdb_io_manager) -> None:
    actual = dimension_media(TEST_RAW_ANILIST_VALID)
    validated = dimension_media_validate_check(actual)
    expected = pd.DataFrame.from_dict(TEST_DIMENSION_MEDIA_VALID)

    assert actual.equals(expected)
    assert validated.passed == True
    assert validated.metadata["count"].value == 1


@mock.patch("dagster_duckdb_pandas.DuckDBPandasIOManager")
def test_dimension_media_invalid(mocked_duckdb_io_manager) -> None:
    actual = dimension_media(TEST_RAW_ANILIST_INVALID)
    validated = dimension_media_validate_check(actual)
    expected = pd.DataFrame.from_dict(TEST_DIMENSION_MEDIA_INVALID)

    assert actual.equals(expected)
    assert validated.passed == False
    assert validated.metadata["count"].value == 0
    assert validated.metadata["error"].value == "no rows processed"


@mock.patch("dagster_duckdb_pandas.DuckDBPandasIOManager")
def test_dimension_user_valid(mocked_duckdb_io_manager) -> None:
    actual = dimension_user(TEST_RAW_ANILIST_VALID)
    validated = dimension_user_validate_check(actual)
    expected = pd.DataFrame.from_dict(TEST_DIMENSION_USER_VALID)

    assert actual.equals(expected)
    assert validated.passed == True
    assert validated.metadata["count"].value == 1


@mock.patch("dagster_duckdb_pandas.DuckDBPandasIOManager")
def test_dimension_user_invalid(mocked_duckdb_io_manager) -> None:
    actual = dimension_user(TEST_RAW_ANILIST_INVALID)
    validated = dimension_user_validate_check(actual)
    expected = pd.DataFrame.from_dict(TEST_DIMENSION_USER_INVALID)

    assert actual.equals(expected)
    assert validated.passed == False
    assert validated.metadata["count"].value == 0
    assert validated.metadata["error"].value == "no rows processed"
