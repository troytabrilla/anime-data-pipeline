import dagster as dg
import requests
import json

from pydantic import Field, BaseModel
from typing import Any
from pathlib import Path
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager
from dagster_dbt import DbtCliResource

from .project import adp_dbt_project


class AniListAPIResource(dg.ConfigurableResource):
    user_name: str = Field(description="User to grab AniList data for")
    query_path: str = Field(description="Path to queries")

    def query(self, query_filename: str) -> Any:
        query_path = Path(self.query_path, query_filename)
        with open(query_path, "r") as query_file:
            query = query_file.read()
            body = {
                "query": query,
                "variables": {
                    "userName": self.user_name,
                },
            }
            res = requests.post("https://graphql.anilist.co", json=body)
            data = res.json()
            return data


class LocalFileJSONIOManager(dg.ConfigurableIOManager):
    data_path: str = Field(description="Path to data directory")

    def get_path(self, context: dg.InputContext | dg.OutputContext) -> Path:
        id_path = context.get_identifier()
        if len(id_path) > 1:
            id_path.pop()
        id_path[-1] = f"{id_path[-1]}.json"
        path = Path(self.data_path, *id_path)
        return path

    def handle_output(self, context: dg.OutputContext, data: Any):
        write_path = self.get_path(context)
        write_path.parent.mkdir(parents=True, exist_ok=True)
        with open(write_path, "w") as json_file:
            if isinstance(data, BaseModel):
                json_file.write(data.model_dump_json())
            else:
                json_file.write(json.dumps(data))

    def load_input(self, context: dg.InputContext) -> Any:
        read_path = self.get_path(context)
        with open(read_path, "r") as json_file:
            raw = json_file.read()
            data = json.loads(raw)
            return data


class ResourceConfig(dg.Config):
    data_path: str = "./data"
    query_path: str = "./queries"
    duckdb_filename: str = "anime_data.duckdb"
    duckdb_schema: str = "pandas"
    anilist_query_filename: str = "anilist.graphql"
    anime_scores_query_filename: str = "anime_scores.sql"
    count_scores_query_filename: str = "count_scores.sql"
    count_scores_genre_query_filename: str = "count_scores_by_top_genre.sql"
    count_scores_tag_query_filename: str = "count_scores_by_top_tag.sql"
    anime_scores_parquet_filename: str = "anime_scores.parquet"


user_name = dg.EnvVar("USER_NAME")
resource_config = ResourceConfig()

resource_defs = dg.Definitions(
    resources={
        "anilist_api": AniListAPIResource(
            user_name=user_name, query_path=resource_config.query_path
        ),
        "duckdb": DuckDBResource(
            database=str(
                Path(resource_config.data_path, resource_config.duckdb_filename)
            ),
        ),
        "local_io_manager": LocalFileJSONIOManager(
            data_path=resource_config.data_path,
        ),
        "duckdb_io_manager": DuckDBPandasIOManager(
            database=str(
                Path(resource_config.data_path, resource_config.duckdb_filename)
            ),
            schema=resource_config.duckdb_schema,
        ),
        "dbt": DbtCliResource(project_dir=adp_dbt_project),
    },
)
