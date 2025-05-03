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
    {{ ref('fact_anime') }}
),
users AS (
  SELECT
    id,
    name
  FROM
    {{ ref('dimension_user') }}
),
media AS (
  SELECT
    id,
    title ->> '$.english' AS english_title,
    title ->> '$.native' AS native_title,
    title ->> '$.romaji' AS romaji_title,
    description,
    UNNEST(synonyms) AS synonym,
    UNNEST(genres) AS genre,
    UNNEST(tags) ->> '$.name' AS tag,
    source,
    episodes,
    season,
    season_year,
    start_date,
    end_date,
    status
  FROM
    {{ ref('dimension_media') }}
)
SELECT
  users.id AS user_id,
  users.name AS user_name,
  media.id AS media_id,
  media.english_title AS english_title,
  media.native_title AS native_title,
  media.romaji_title AS romaji_title,
  media.description AS description,
  media.synonym AS synonym,
  media.genre AS genre,
  media.tag AS tag,
  media.source AS source,
  media.episodes AS episodes,
  media.season AS season,
  media.season_year AS season_year,
  media.start_date AS start_date,
  media.end_date AS end_date,
  media.status AS status,
  stats.progress AS progress,
  stats.watch_status AS watch_status,
  stats.score AS score,
  stats.average_score AS average_score,
  stats.mean_score AS mean_score,
  stats.popularity AS popularity,
  stats.trending AS trending,
  stats.favourites AS favourites
FROM
  stats
  JOIN users ON stats.user_id = users.id
  JOIN media ON stats.media_id = media.id
