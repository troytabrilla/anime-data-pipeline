WITH stats AS (
  SELECT
    tag,
    score,
    COUNT(*) AS count,
    ROW_NUMBER() OVER (PARTITION BY score ORDER BY count DESC) AS rank
  FROM
    dbt.anime_scores
  WHERE
    tag IS NOT NULL AND score > 0.0
  GROUP BY
    tag, score
  ORDER BY
    count DESC, score DESC
)
SELECT
  *
FROM
  stats
WHERE
  rank <= 20;
