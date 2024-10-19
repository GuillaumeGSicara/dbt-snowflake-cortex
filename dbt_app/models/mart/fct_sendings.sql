SELECT
    send_id AS sending_id,
    customer_id AS customer_id,
    campaign_id AS campaign_id,
    send_date AS sent_at
FROM {{ source('raw_layer', 'SENDS')}}