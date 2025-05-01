WITH stats AS (
  SELECT
    media_id,
    user_id,
    progress,
    watch_status,
    score,
    average_score,
    mean_score,
    popularity,
    trending,
    favourites
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
    title ->> '$.english' AS english_title,
    title ->> '$.native' AS native_title,
    title ->> '$.romaji' AS romaji_title,
    description,
    UNNEST (synonyms) AS synonym,
    UNNEST (genres) AS genre,
    UNNEST (tags) ->> '$.name' AS tag,
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
