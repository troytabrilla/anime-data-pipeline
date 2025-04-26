import dagster as dg
import json

from pydantic import ValidationError

from .resources import AniListAPIResource
from ..lib import schemas

log = dg.get_dagster_logger()


class RawConfig(dg.Config):
    raw_json_filename: str = "raw.json"


@dg.asset(group_name="ingest", io_manager_key="local_io_manager")
def raw_anilist(anilist_api: AniListAPIResource) -> dg.Output:
    log.info(f"Loading raw anilist data for user {anilist_api.user_name}.")
    data = anilist_api.query()
    size = len(bytes(json.dumps(data).encode()))
    metadata = {"user_name": anilist_api.user_name, "size": size}
    return dg.Output(value=data, metadata=metadata)


@dg.asset_check(asset=raw_anilist)
def raw_anilist_validate_check(raw_anilist: dg.Output) -> dg.AssetCheckResult:
    try:
        schemas.Raw.model_validate(raw_anilist)
        return dg.AssetCheckResult(passed=True)
    except ValidationError as err:
        log.error(err)
        metadata = {"err": "raw_anilist validation failed"}
        return dg.AssetCheckResult(passed=False, metadata=metadata)


# TODO add assets for flattened anime list and user
# TODO add assets for duckdb and postgres
# TODO add asset checks
