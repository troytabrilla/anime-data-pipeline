{% macro convert_to_date(column_name) %}
  IF(
    ((entry -> '$.{{ column_name }}.day')::int64 IS NOT NULL) AND ((entry -> '$.{{ column_name }}.month')::int64 IS NOT NULL) AND ((entry -> '$.{{ column_name }}.day')::int64 IS NOT NULL),
    CONCAT(entry -> '$.{{ column_name }}.year', '-', entry -> '$.{{ column_name }}.month', '-', entry -> '$.{{ column_name }}.day')::DATE,
    NULL
  )
{% endmacro %}
