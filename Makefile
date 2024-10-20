upload-semantic-model:
	snow stage copy ./streamlit_app/semantic_models/dbt_app.yml \
		--database=DBT_CORTEX \
		--schema=DEFINITIONS @dbt_app \
		--connection=DEMO_CORTEX_ACCOUNT_ADMIN \
		--overwrite