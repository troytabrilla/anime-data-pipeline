import dagster as dg

from .jobs import anilist_job

anilist_schedule = dg.ScheduleDefinition(
    name="anilist",
    target=dg.AssetSelection.groups("ingest", "transform"),
    cron_schedule="*/30 * * * * ",
)

schedule_defs = dg.Definitions(schedules=[anilist_schedule])
