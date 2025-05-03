WITH source AS (
  SELECT
    data -> '$.User' AS data
  FROM
    {{ source('dbt', 'raw_anilist') }}
)
SELECT
  *
FROM
  source
