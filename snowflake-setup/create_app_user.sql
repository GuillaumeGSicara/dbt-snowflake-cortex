CREATE OR REPLACE USER billy_bat
  PASSWORD = 'billy_bat2046'
  DEFAULT_ROLE = ACCOUNTADMIN
  DEFAULT_WAREHOUSE = 'COMPUTE_WH'
  DEFAULT_NAMESPACE = 'SNOWFLAKE_SAMPLE_DATA.TPCH_SF10'
  MUST_CHANGE_PASSWORD = FALSE;