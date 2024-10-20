
upload-semantic-models:
	snow stage copy ./streamlit_app/semantic_models/dbt_app.yml \
		--database=DBT_CORTEX \
		--schema=DEFINITIONS \
		--connection=DEMO_CORTEX_ACCOUNT_ADMIN \
		--overwrite \
		@dbt_app;

	snow stage copy ./streamlit_app/semantic_models/semantic_rpt_tag_campaigns_sends.yml \
		--database=DBT_CORTEX \
		--schema=DEFINITIONS \
		--connection=DEMO_CORTEX_ACCOUNT_ADMIN \
		--overwrite \
		@semantic_rpt_tag_campaigns_sends