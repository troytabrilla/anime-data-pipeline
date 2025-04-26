import dagster as dg

anilist_job = dg.define_asset_job(name="anilist_job")

anilist_job_defs = dg.Definitions(
    jobs=[anilist_job],
)
