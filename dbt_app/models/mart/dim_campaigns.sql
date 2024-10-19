SELECT
    DISTINCT
    campaign_id,
    name AS campaign_name,
    created_at AS campaign_created_at
FROM {{ ref('src_campaigns_info') }}