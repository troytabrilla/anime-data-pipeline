import dagster as dg
import pandas as pd
import json
import re

from pydantic import ValidationError, BaseModel
from dagster_duckdb import DuckDBResource
from dagster_dbt import DbtCliResource, dbt_assets
from typing import Any
from pathlib import Path

from .resources import AniListAPIResource, ResourceConfig
from .project import adp_dbt_project
from ..lib import schemas

log = dg.get_dagster_logger()


@dg.asset(
    group_name="setup",
)
def ensure_data_exists(
    duckdb: DuckDBResource, config: ResourceConfig
) -> dg.MaterializeResult:
    Path(config.data_path).mkdir(parents=True, exist_ok=True)
    with duckdb.get_connection() as conn:
        conn.execute("SELECT 1;")
        metadata = {
            "success": True,
            "msg": "created data directory and Duckdb database",
        }
        return dg.MaterializeResult(metadata=metadata)


@dg.asset(
    group_name="ingest",
    kinds={"python"},
    io_manager_key="local_io_manager",
    deps=[ensure_data_exists],
)
def raw_anilist(anilist_api: AniListAPIResource, config: ResourceConfig) -> dg.Output:
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


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    df.columns = [pattern.sub("_", name).lower() for name in df.columns]
    if "score" in df.columns:
        df["score"] = df["score"] / 1.0
    if "average_score" in df.columns:
        df["average_score"] = df["average_score"] / 10.0
    if "mean_score" in df.columns:
        df["mean_score"] = df["mean_score"] / 10.0
    if "episodes" in df.columns:
        df["episodes"] = df["episodes"].astype("Int64")
    if "season_year" in df.columns:
        df["season_year"] = df["season_year"].astype("Int64")
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
        df = normalize_df(df)

        return df
    except KeyError as err:
        log.error(err)
        return pd.DataFrame()


def validate_dataframe(df: pd.DataFrame) -> dg.AssetCheckResult:
    rows = len(df)
    preview = df.tail().drop(
        ["stats", "rankings", "statistics", "genres", "tags", "synonyms"],
        axis=1,
        errors="ignore",
    )
    metadata = {
        "rows": dg.MetadataValue.int(rows),
        "preview": dg.MetadataValue.md(preview.to_markdown()),
    }
    if rows == 0:
        metadata["error"] = "no rows processed"
    return dg.AssetCheckResult(passed=rows > 0, metadata=metadata)


@dg.asset(
    group_name="pandas",
    kinds={"duckdb", "pandas"},
    io_manager_key="duckdb_io_manager",
    deps=[raw_anilist],
)
def fact_anime(raw_anilist: Any) -> pd.DataFrame:
    return convert_anilist_json_to_model(raw_anilist, schemas.FactAnime)


@dg.asset_check(asset=fact_anime, blocking=True)
def fact_anime_validate_check(fact_anime: pd.DataFrame) -> dg.AssetCheckResult:
    return validate_dataframe(fact_anime)


@dg.asset(
    group_name="pandas",
    kinds={"duckdb", "pandas"},
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
    group_name="pandas",
    kinds={"duckdb", "pandas"},
    io_manager_key="duckdb_io_manager",
    deps=[raw_anilist],
)
def dimension_user(raw_anilist: Any) -> pd.DataFrame:
    try:
        user = raw_anilist["data"]["User"]
        models = [schemas.DimensionUser.model_validate(user).model_dump()]

        log.debug(models)

        df = pd.DataFrame.from_dict(models)
        df = normalize_df(df)

        return df
    except KeyError as err:
        log.error(err)
        return pd.DataFrame()


@dg.asset_check(asset=dimension_user, blocking=True)
def dimension_user_validate_check(dimension_user: pd.DataFrame) -> dg.AssetCheckResult:
    return validate_dataframe(dimension_user)


@dg.asset(
    group_name="pandas",
    kinds={"duckdb", "pandas"},
    deps=[fact_anime, dimension_media, dimension_user],
    automation_condition=dg.AutomationCondition.eager(),
)
def anime_scores(duckdb: DuckDBResource, config: ResourceConfig) -> pd.DataFrame:
    query_path = Path(config.query_path, config.anime_score_query_filename)
    with open(query_path, "r") as query_file:
        query = query_file.read()

        with duckdb.get_connection() as conn:
            conn.execute(
                f"""
                CREATE OR REPLACE VIEW
                    {config.duckdb_schema}.anime_scores
                AS
                    {query}
                """
            )

            df = conn.execute(
                f"""
                SELECT
                    *
                FROM
                    {config.duckdb_schema}.anime_scores;
                """
            ).fetchdf()

            log.debug(df.tail())

            return df


@dg.asset_check(asset=anime_scores, blocking=True)
def anime_scores_validate_check(anime_scores: pd.DataFrame) -> dg.AssetCheckResult:
    return validate_dataframe(anime_scores)


class DBTConfig(ResourceConfig):
    raw_json_filename: str = "raw_anilist.json"
    dbt_schema: str = "dbt"
    dbt_raw_table: str = "raw_anilist"


@dg.asset(
    group_name="dbt",
    kinds={"duckdb"},
    deps=[raw_anilist],
)
def dbt_raw(
    context: dg.AssetExecutionContext,
    duckdb: DuckDBResource,
    config: DBTConfig,
) -> None:
    run_id = context.run.run_id
    raw_anilist_json_filepath = Path(config.data_path, run_id, config.raw_json_filename)

    with duckdb.get_connection() as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {config.dbt_schema};")
        conn.execute(
            f"CREATE OR REPLACE TABLE {config.dbt_schema}.{config.dbt_raw_table} AS SELECT * FROM '{raw_anilist_json_filepath}'"
        )


@dg.asset_check(asset=dbt_raw, blocking=True)
def dbt_raw_validate_check(
    duckdb: DuckDBResource, config: DBTConfig
) -> dg.AssetCheckResult:
    with duckdb.get_connection() as conn:
        results = conn.execute(
            f"SELECT COUNT(*) FROM {config.dbt_schema}.{config.dbt_raw_table}"
        ).fetchone()
        rows = results[0]
    metadata = {"rows": dg.MetadataValue.int(rows)}
    if rows == 0:
        metadata["error"] = "no rows processed"
    return dg.AssetCheckResult(passed=rows == 1, metadata=metadata)


@dbt_assets(manifest=adp_dbt_project.manifest_path)
def adp_dbt_dbt_assets(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


# TODO add job to show graphs of scores by genres/tags
# TODO save results/db to external persistent storage?
