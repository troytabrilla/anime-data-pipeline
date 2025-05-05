SELECT
  score,
  COUNT(DISTINCT(media_id)) AS count
FROM
  dbt.anime_scores
WHERE
  score > 0.0
GROUP BY
  score
ORDER BY
  count DESC, score DESC;
