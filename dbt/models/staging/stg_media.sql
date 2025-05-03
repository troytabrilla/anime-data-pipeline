WITH source AS (
  SELECT
    data -> '$.MediaListCollection' AS data
  FROM
    {{ source('dbt', 'raw_anilist') }}
)
SELECT
  *
FROM
  source
