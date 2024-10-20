SELECT
    dim_tags.tag_name,
    dim_campaigns.campaign_id,
    dim_campaigns.campaign_name,
    COUNT(fct_sendings.sending_id) as nb_sends,
    COUNT(DISTINCT fct_sendings.customer_id) AS nb_customers_sent_to
FROM {{ ref("dim_tags") }} dim_tags
JOIN {{ ref("brg_tags_to_campaigns") }} brg_tags_to_campaigns
    ON dim_tags.tag_id = brg_tags_to_campaigns.tag_id
JOIN {{ ref("dim_campaigns") }} dim_campaigns
    ON brg_tags_to_campaigns.campaign_id = dim_campaigns.campaign_id
JOIN {{ ref("fct_sendings")}} fct_sendings
    ON dim_campaigns.campaign_id = fct_sendings.campaign_id
GROUP BY
    dim_tags.tag_name,
    dim_campaigns.campaign_id,
    dim_campaigns.campaign_name
