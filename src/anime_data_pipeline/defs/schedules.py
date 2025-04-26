import dagster as dg

from .jobs import anilist_job

anilist_hourly_schedule = dg.ScheduleDefinition(
    name="anilist_hourly",
    job=anilist_job,
    cron_schedule="0 * * * * ",
)

schedule_defs = dg.Definitions(schedules=[anilist_hourly_schedule])
