WITH lists AS (
  SELECT
    UNNEST((data -> '$.lists[*].entries[*]')::JSON[]) AS entry
  FROM
    {{ ref('stg_media') }}
)
SELECT
  (entry -> '$.media.id')::INT64 AS id,
  (entry -> '$.media.genres')::VARCHAR[] AS genres,
  (entry ->> '$.media.description') AS description,
  (entry ->> '$.media.coverImage.extraLarge') AS cover_image,
  (entry ->> '$.media.type') AS type,
  (entry -> '$.media.tags')::JSON[] AS tags,
  (entry -> '$.media.episodes')::INT64 AS episodes,
  (entry ->> '$.media.format') AS format,
  (entry ->> '$.media.season') AS season,
  (entry ->> '$.media.seasonYear')::INT64 AS season_year,
  {{ convert_to_date('media.startDate') }} AS start_date,
  {{ convert_to_date('media.endDate') }} AS end_date,
  (entry -> '$.media.synonyms')::VARCHAR[] AS synonyms,
  (entry -> '$.media.title') AS title,
  (entry ->> '$.media.source') AS source,
  (entry ->> '$.media.bannerImage') AS banner_image,
  (entry ->> '$.media.siteUrl') AS site_url,
  (entry ->> '$.media.status') AS status
FROM
  lists
