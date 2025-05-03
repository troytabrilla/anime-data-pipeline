WITH source AS (
  SELECT
    data -> '$.User' AS data
  FROM
    {{ source('anime_data', 'raw_anilist') }}
)
SELECT
  *
FROM
  source
