WITH stats AS (
  SELECT
    COUNT(*) AS count,
    tag,
    score,
    ROW_NUMBER() OVER (PARTITION BY score ORDER BY count DESC) AS rank
  FROM
    dbt.anime_scores
  WHERE
    tag IS NOT NULL AND score > 0.0
  GROUP BY
    tag, score
  ORDER BY
    count DESC
)
SELECT
  *
FROM
  stats
WHERE
  rank <= 20;
