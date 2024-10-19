SELECT
    DISTINCT
    {{ dbt_utils.generate_surrogate_key(('tag',))}} AS tag_id,
    tag AS tag_name
FROM {{ ref('stg_tags_and_campaigns') }}