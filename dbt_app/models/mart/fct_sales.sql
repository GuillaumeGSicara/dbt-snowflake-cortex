SELECT
    purchase_id AS sale_id,
    customer_id AS customer_id,
    product AS product_name,
    purchased_at AS sold_at
FROM {{ source('raw_layer', 'SALES')}}