SELECT
    DISTINCT
    CAMPAIGN_ID,
    {{ dbt_utils.generate_surrogate_key(('tag',))}} AS tag_id
FROM {{ ref('stg_tags_and_campaigns') }}