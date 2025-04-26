WITH
  stats AS (
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
      title,
      description,
      synonyms,
      genres,
      tags,
      source,
      episodes,
      season,
      season_year,
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
