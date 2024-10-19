import os
import json
import yaml
import snowflake.connector

from pathlib import Path
from snowflake.connector import SnowflakeConnection


MAX_VALUES_SIZE = 16_384
DB_NAME = "DBT_CORTEX"
SCHEMA_NAME = "RAW"
TABLE_NAMES_TO_RAW_FILES = {
    "CAMPAIGNS": Path(__file__).parent / "data/raw_campaigns.json",
    "CUSTOMERS": Path(__file__).parent / "data/raw_customers.json",
    "SENDS": Path(__file__).parent / "data/raw_sends.json",
    "SALES": Path(__file__).parent / "data/raw_sales.json",
}


def get_dbt_connection_info(profile_name: str, target_name: str) -> dict[str, str]:
    profiles_path = os.path.expanduser('~/.dbt/profiles.yml')
    with open(profiles_path, 'r') as file:
        profiles = yaml.safe_load(file)

    return profiles.get(profile_name, {}).get('outputs', {}).get(target_name, {})

def get_connection() -> SnowflakeConnection:
    dbt_conn = get_dbt_connection_info(
        profile_name='cortex-profile',
        target_name='dev'
    )
    return snowflake.connector.connect(
        user=dbt_conn["user"],
        password=dbt_conn["password"],
        account=dbt_conn["account"],
        session_parameters={
            'QUERY_TAG': 'PYTHON_DATA_LOADER',
    }
)

def empty_table(
        conn: SnowflakeConnection,
        db_name: str,
        schema_name: str,
        table_name: str) -> None:

    conn.cursor().execute(f"DELETE FROM {db_name}.{schema_name}.{table_name}")

def prepare_value_for_snowflake_insert(dict_value: str | list | int) -> str:
    if isinstance(dict_value, str):
        return "'" + str(dict_value).replace("'", "''").replace('"', "'") + "'"
    elif isinstance(dict_value, list):
        return "'" + json.dumps(dict_value).replace('"', "''") + "'"
    else:
        return str(dict_value)

def load_table_from_raw_file(
    conn: SnowflakeConnection,
    db_name: str,
    schema_name: str,
    table_name: str,
    raw_file_name
    ) -> None:

    # TODO: chunk based on max size of VALUES for an SQL statement

    with open(raw_file_name, 'r') as raw_file:
        raw_data: list[dict] = json.loads(raw_file.read())

    columns = ', '.join(raw_data[0].keys())
    columns_select = ', '.join(
        column_name if not isinstance(column_value, list) else f'PARSE_JSON({column_name})'
        for column_name, column_value in raw_data[0].items()
    )

    values_str = []
    for row in raw_data:
        values_str.append(
            prepare_value_for_snowflake_insert(dict_value=dict_value)
            for dict_value in row.values()
        )

    values = ', '.join(f"({', '.join(row_values)})" for row_values in values_str)

    sql = (
        f"INSERT INTO {db_name}.{schema_name}.{table_name} ({columns}) "
        f"SELECT {columns_select} FROM VALUES {values}"
        f"AS t({columns})"
    )


    conn.cursor().execute(sql)

if __name__ == "__main__":
    conn = get_connection()
    for table in TABLE_NAMES_TO_RAW_FILES.keys():
        empty_table(conn, DB_NAME, SCHEMA_NAME, table)
        load_table_from_raw_file(
            conn,
            DB_NAME,
            SCHEMA_NAME,
            table,
            TABLE_NAMES_TO_RAW_FILES[table]
        )