import dagster as dg
import pandas as pd
import json

from pydantic import ValidationError, BaseModel
from typing import Any

from .resources import AniListAPIResource
from ..lib import schemas

log = dg.get_dagster_logger()


class RawConfig(dg.Config):
    raw_json_filename: str = "raw.json"


@dg.asset(group_name="ingest", compute_kind="json", io_manager_key="local_io_manager")
def raw_anilist(anilist_api: AniListAPIResource) -> dg.Output:
    data = anilist_api.query()
    metadata = {
        "user_name": anilist_api.user_name,
    }
    return dg.Output(value=data, metadata=metadata)


@dg.asset_check(asset=raw_anilist, blocking=True)
def raw_anilist_validate_check(raw_anilist: dg.Output) -> dg.AssetCheckResult:
    try:
        schemas.Raw.model_validate(raw_anilist)
        size = len(bytes(json.dumps(raw_anilist).encode()))
        metadata = {
            "size": dg.MetadataValue.int(size),
        }
        return dg.AssetCheckResult(passed=True, metadata=metadata)
    except ValidationError as err:
        log.error(err)
        metadata = {
            "error": dg.MetadataValue.text("raw_anilist validation failed"),
        }
        return dg.AssetCheckResult(passed=False, metadata=metadata)


def convert_anilist_json_to_model(data: Any, model: type[BaseModel]):
    lists = data["data"]["MediaListCollection"]["lists"]

    models = []
    for lst in lists:
        for entry in lst["entries"]:
            try:
                media = entry["media"]
                status = media["status"]
                watch_status = entry["status"]
                data = (
                    media
                    | entry
                    | {
                        "status": status,
                        "watchStatus": watch_status,
                    }
                )
                fact = model.model_validate(data).model_dump()
                models.append(fact)
            except ValidationError as err:
                log.error(err)

    log.debug(models[:5])

    return pd.DataFrame.from_dict(models)


def validate_dataframe(df: pd.DataFrame) -> dg.AssetCheckResult:
    count = len(df)
    preview = df.tail().drop(
        ["stats", "rankings", "statistics", "genres", "tags", "synonyms"],
        axis=1,
        errors="ignore",
    )
    metadata = {
        "count": dg.MetadataValue.int(count),
        "preview": dg.MetadataValue.md(preview.to_markdown()),
    }
    if count == 0:
        metadata["error"] = "no rows processed"
    return dg.AssetCheckResult(passed=count > 0, metadata=metadata)


@dg.asset(
    group_name="transform",
    compute_kind="duckdb",
    io_manager_key="duckdb_io_manager",
    deps=[raw_anilist],
)
def fact_anime(raw_anilist: Any) -> pd.DataFrame:
    return convert_anilist_json_to_model(raw_anilist, schemas.FactAnime)


@dg.asset_check(asset=fact_anime, blocking=True)
def fact_anime_validate_check(fact_anime: pd.DataFrame) -> dg.AssetCheckResult:
    return validate_dataframe(fact_anime)


@dg.asset(
    group_name="transform",
    compute_kind="duckdb",
    io_manager_key="duckdb_io_manager",
    deps=[raw_anilist],
)
def dimension_media(raw_anilist: Any) -> pd.DataFrame:
    return convert_anilist_json_to_model(raw_anilist, schemas.DimensionMedia)


@dg.asset_check(asset=dimension_media, blocking=True)
def dimension_media_validate_check(
    dimension_media: pd.DataFrame,
) -> dg.AssetCheckResult:
    return validate_dataframe(dimension_media)


@dg.asset(
    group_name="transform",
    compute_kind="duckdb",
    io_manager_key="duckdb_io_manager",
    deps=[raw_anilist],
)
def dimension_user(raw_anilist: Any) -> pd.DataFrame:
    user = raw_anilist["data"]["User"]
    models = [schemas.DimensionUser.model_validate(user).model_dump()]

    log.debug(models)

    return pd.DataFrame.from_dict(models)


@dg.asset_check(asset=dimension_user, blocking=True)
def dimension_user_validate_check(dimension_user: pd.DataFrame) -> dg.AssetCheckResult:
    return validate_dataframe(dimension_user)


# TODO add assets for analytics (e.g. scores by genre and tag, histogram by genre and tag, histogram by score, etc)
# TODO materialize analytics assets when dependencies update
# TODO add assets for postgres?
