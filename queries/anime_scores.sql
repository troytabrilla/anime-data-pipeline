WITH stats AS (
  SELECT
    media_id,
    user_id,
    progress,
    watch_status,
    CAST(score AS DOUBLE) AS score,
    average_score / 10.0 AS average_score,
    mean_score / 10.0 AS mean_score,
    popularity,
    trending favourites
  FROM
    fact_anime
),
users AS (
  SELECT
    id,
    name
  FROM
    dimension_user
),
media AS (
  SELECT
    id,
    CAST(title -> '$.english' AS VARCHAR) AS english_title,
    CAST(title -> '$.native' AS VARCHAR) AS native_title,
    CAST(title -> '$.romaji' AS VARCHAR) AS romaji_title,
    description,
    UNNEST (synonyms) AS synonym,
    UNNEST (genres) AS genre,
    REPLACE(
      CAST(UNNEST (tags) -> '$.name' AS VARCHAR),
      '"',
      ''
    ) AS tag,
    source,
    CAST(episodes AS INT) AS episodes,
    season,
    CAST(season_year AS INT) AS season_year,
    start_date,
    end_date,
    status
  FROM
    dimension_media
)
SELECT
  *
FROM
  stats
  JOIN users ON stats.user_id = users.id
  JOIN media ON stats.media_id = media.id;
