WITH source AS (
  SELECT
    data -> '$.MediaListCollection' AS data
  FROM
    {{ source('anime_data', 'raw_anilist') }}
)
SELECT
  *
FROM
  source
