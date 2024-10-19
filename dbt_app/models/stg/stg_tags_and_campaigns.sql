SELECT
    DISTINCT
    campaign_id,
    TO_VARCHAR(value) AS tag
FROM {{ source('raw_layer', 'CAMPAIGNS')}},
    LATERAL FLATTEN(input => tags)