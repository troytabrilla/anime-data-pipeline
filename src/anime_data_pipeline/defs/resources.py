import dagster as dg
import requests
import json

from pydantic import Field, BaseModel
from typing import Any
from pathlib import Path
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager


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


user_name = dg.EnvVar("USER_NAME")
data_path = dg.EnvVar("DATA_PATH")
query_path = dg.EnvVar("QUERY_PATH")
duckdb_path = dg.EnvVar("DUCKDB_PATH")

resource_defs = dg.Definitions(
    resources={
        "anilist_api": AniListAPIResource(user_name=user_name, query_path=query_path),
        "duckdb": DuckDBResource(database=duckdb_path),
        "local_io_manager": LocalFileJSONIOManager(
            data_path=data_path,
        ),
        "duckdb_io_manager": DuckDBPandasIOManager(
            database=duckdb_path,
            schema="anilist",
        ),
    },
)
