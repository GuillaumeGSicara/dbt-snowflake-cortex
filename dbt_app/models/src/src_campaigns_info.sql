SELECT
    campaign_id,
    name,
    created_at
FROM {{ source('raw_layer', 'CAMPAIGNS')}}