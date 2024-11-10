WITH campaign_id_tag AS (
    SELECT
        brg_tags_to_campaigns.campaign_id,
        ARRAY_AGG(DISTINCT tag_name) AS tag_names
    FROM {{ ref('brg_tags_to_campaigns') }} AS brg_tags_to_campaigns
    JOIN {{ ref('dim_tags') }} AS dim_tags
        ON brg_tags_to_campaigns.tag_id = dim_tags.tag_id
    GROUP BY
        brg_tags_to_campaigns.campaign_id
),
per_customer_send_information AS (
    SELECT
        customer_id,
        COUNT(DISTINCT fct_sendings.sending_id) AS number_of_sendings,
        COUNT(DISTINCT dim_campaigns.campaign_id) AS number_of_campaigns,
        ARRAY_AGG(DISTINCT dim_campaigns.campaign_name) AS campaign_names,
        ARRAY_UNION_AGG(tag_names) AS tag_names,
    FROM {{ ref('fct_sendings') }} AS fct_sendings
    LEFT JOIN {{ ref('dim_campaigns') }} AS dim_campaigns
        ON fct_sendings.campaign_id = dim_campaigns.campaign_id
    LEFT JOIN campaign_id_tag
        ON dim_campaigns.campaign_id = campaign_id_tag.campaign_id
    GROUP BY
        customer_id
),
per_customer_sales_information AS (
    SELECT
        customer_id,
        COUNT(DISTINCT fct_sales.sale_id) AS number_of_purchases,
        ARRAY_AGG(DISTINCT fct_sales.product_name) AS product_names,
        MIN(sold_at) AS first_purchase_date,
        MAX(sold_at) AS last_purchase_date,
        DATEDIFF(DAY, CURRENT_DATE(), MAX(sold_at)) AS time_since_last_purchase
    FROM {{ ref('fct_sales') }}  AS fct_sales
    GROUP BY
        customer_id
)
SELECT
    dim_customers.customer_id,
    dim_customers.customer_full_name,
    dim_customers.customer_email,
    dim_customers.customer_country,
    -- Send information
    COALESCE(per_customer_send_information.number_of_sendings, 0) AS number_of_sendings,
    COALESCE(per_customer_send_information.number_of_campaigns, 0) AS number_of_campaigns,
    COALESCE(per_customer_send_information.campaign_names, []) AS campaign_names,
    COALESCE(per_customer_send_information.tag_names, []) AS tag_names,
    -- Sales information
    COALESCE(per_customer_sales_information.number_of_purchases, 0) AS number_of_purchases,
    COALESCE(per_customer_sales_information.product_names, []) AS product_names,
    per_customer_sales_information.first_purchase_date,
    per_customer_sales_information.last_purchase_date,
    per_customer_sales_information.time_since_last_purchase
FROM {{ ref('dim_customers') }}  AS dim_customers
LEFT JOIN per_customer_send_information
    ON dim_customers.customer_id = per_customer_send_information.customer_id
LEFT JOIN per_customer_sales_information
    ON dim_customers.customer_id = per_customer_sales_information.customer_id