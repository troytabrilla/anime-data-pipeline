import dagster as dg

from typing import Any

from .resources import AniListAPIResource
from ..lib import schemas


class RawConfig(dg.Config):
    raw_json_filename: str = "raw.json"


@dg.asset
def raw_anilist(
    context: dg.AssetExecutionContext,
    anilist_api: AniListAPIResource,
) -> Any:
    context.log.info(f"Loading raw anilist data for user {anilist_api.user_name}.")
    data = anilist_api.query()
    schemas.RawModel.model_validate(data)
    return data
