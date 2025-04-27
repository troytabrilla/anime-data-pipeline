import dagster as dg
import pandas as pd
import json
import re

from pydantic import ValidationError, BaseModel
from dagster_duckdb import DuckDBResource
from typing import Any
from pathlib import Path

from .resources import AniListAPIResource
from ..lib import schemas

log = dg.get_dagster_logger()


class IngestConfig(dg.Config):
    anilist_query_filename: str = "anilist.graphql"


@dg.asset(group_name="ingest", compute_kind="json", io_manager_key="local_io_manager")
def raw_anilist(anilist_api: AniListAPIResource, config: IngestConfig) -> dg.Output:
    data = anilist_api.query(config.anilist_query_filename)
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


def update_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    df.columns = [pattern.sub("_", name).lower() for name in df.columns]
    return df


def convert_anilist_json_to_model(data: Any, model: type[BaseModel]) -> pd.DataFrame:
    try:
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

        df = pd.DataFrame.from_dict(models)
        df = update_df_columns(df)

        return df
    except KeyError as err:
        log.error(err)
        return pd.DataFrame()


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
    try:
        user = raw_anilist["data"]["User"]
        models = [schemas.DimensionUser.model_validate(user).model_dump()]

        log.debug(models)

        df = pd.DataFrame.from_dict(models)
        df = update_df_columns(df)

        return df
    except KeyError as err:
        log.error(err)
        return pd.DataFrame()


@dg.asset_check(asset=dimension_user, blocking=True)
def dimension_user_validate_check(dimension_user: pd.DataFrame) -> dg.AssetCheckResult:
    return validate_dataframe(dimension_user)


class AnalysisConfig(dg.Config):
    duckdb_schema: str = "local.anilist"
    query_path: str = dg.EnvVar("QUERY_PATH")
    query_name: str = "anime_scores.sql"


@dg.asset(
    group_name="analysis",
    compute_kind="duckdb",
    deps=[fact_anime, dimension_media, dimension_user],
    automation_condition=dg.AutomationCondition.eager(),
)
def anime_scores(duckdb: DuckDBResource, config: AnalysisConfig) -> pd.DataFrame:
    query_path = Path(config.query_path, config.query_name)
    with open(query_path, "r") as query_file:
        query = query_file.read()

        with duckdb.get_connection() as conn:
            conn.execute(
                f"""
                USE {config.duckdb_schema};
                CREATE OR REPLACE VIEW
                    anime_scores
                AS
                    {query}
                """
            )

            df = conn.execute(
                f"""
                USE {config.duckdb_schema};
                SELECT
                    *
                FROM
                    anime_scores;
                """
            ).fetchdf()

            log.debug(df.tail())

            return df


@dg.asset_check(asset=anime_scores, blocking=True)
def anime_scores_validate_check(anime_scores: pd.DataFrame) -> dg.AssetCheckResult:
    return validate_dataframe(anime_scores)
