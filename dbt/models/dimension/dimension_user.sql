SELECT
  (data -> '$.id')::INT64 AS id,
  data ->> '$.name' AS name,
  data ->> '$.avatar.large' AS avatar,
  data ->> '$.bannerImage' AS banner_image,
  data ->> '$.siteUrl' AS site_url,
  data -> '$.statistics' AS statistics
FROM
  {{ ref('stg_user') }}
