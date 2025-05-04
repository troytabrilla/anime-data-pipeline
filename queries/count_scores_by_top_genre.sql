WITH stats AS (
  SELECT
    COUNT(*) AS count,
    genre,
    score,
    ROW_NUMBER() OVER (PARTITION BY score ORDER BY count DESC) AS rank
  FROM
    dbt.anime_scores
  WHERE
    genre IS NOT NULL AND score > 0.0
  GROUP BY
    genre, score
  ORDER BY
    count DESC
)
SELECT
  *
FROM
  stats
WHERE
  rank <= 10;
