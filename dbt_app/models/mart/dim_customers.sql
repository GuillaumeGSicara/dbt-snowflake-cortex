SELECT
    customer_id AS customer_id,
    full_name AS customer_full_name,
    first_name AS customer_first_name,
    last_name AS customer_last_name,
    email AS customer_email,
    country AS customer_country,
FROM {{ source('raw_layer', 'CUSTOMERS')}}