SELECT
  COUNT(DISTINCT(media_id)) AS count,
  score
FROM
  dbt.anime_scores
WHERE
  score > 0.0
GROUP BY
  score
ORDER BY
  count DESC;
