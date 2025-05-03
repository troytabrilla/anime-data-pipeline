WITH lists AS (
  SELECT
    UNNEST((data -> '$.lists[*].entries[*]')::JSON[]) AS entry
  FROM
    {{ ref('stg_media') }}
)
SELECT
  (entry -> '$.id')::INT64 AS id,
  (entry -> '$.userId')::INT64 AS user_id,
  (entry -> '$.media.id')::INT64 AS media_id,
  (entry -> '$.media.averageScore')::DOUBLE / 10.0 AS average_score,
  (entry -> '$.media.meanScore')::DOUBLE / 10.0 AS mean_score,
  (entry -> '$.media.popularity')::INT64 AS popularity,
  (entry -> '$.media.trending')::INT64 AS trending,
  (entry -> '$.media.favourites')::INT64 AS favourites,
  (entry -> '$.progress')::INT64 AS progress,
  (entry -> '$.media.episodes')::INT64 AS episodes,
  (entry -> '$.score')::DOUBLE AS score,
  (entry ->> '$.status') AS watch_status,
  {{ convert_to_date('startedAt') }} AS started_at,
  {{ convert_to_date('completedAt') }} AS completed_at,
  (entry -> '$.media.stats') AS stats,
  (entry -> '$.media.rankings') AS rankings
FROM
  lists
