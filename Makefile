upload-semantic-models:
	snow stage copy ./SiS/semantic_models/dbt_app.yml \
		--database=DBT_CORTEX \
		--schema=DEFINITIONS \
		--connection=DEMO_CORTEX_ACCOUNT_ADMIN \
		--overwrite \
		@dbt_app;

	snow stage copy ./SiS/semantic_models/semantic_rpt_tag_campaigns_sends.yml \
		--database=DBT_CORTEX \
		--schema=DEFINITIONS \
		--connection=DEMO_CORTEX_ACCOUNT_ADMIN \
		--overwrite \
		@semantic_rpt_tag_campaigns_sends

	snow stage copy ./SiS/semantic_models/semantic_rpt_customer_informations.yml \
		--database=DBT_CORTEX \
		--schema=DEFINITIONS \
		--connection=DEMO_CORTEX_ACCOUNT_ADMIN \
		--overwrite \
		@semantic_rpt_customer_informations

deploy-streamlit-app:
	cd ./SiS/app && \
	snow streamlit deploy cortex_analyst_demo \
		--replace
