SELECT
    DISTINCT
    campaign_id,
    name AS campaign_name,
    CAST(created_at AS DATETIME) AS campaign_created_at
FROM {{ ref('src_campaigns_info') }}