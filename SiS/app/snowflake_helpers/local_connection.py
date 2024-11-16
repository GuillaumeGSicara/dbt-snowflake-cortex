import os
import toml  # type: ignore
from typing import Dict
from snowflake.snowpark.session import Session

def get_snowflake_connection_info(profile_name: str,) -> Dict[str, str]:
    snowflake_connections_path = os.path.expanduser('~/.snowflake/config.toml')
    with open(snowflake_connections_path, 'r') as file:
        connections = toml.load(file)
        if profile_name not in connections["connections"]:
            raise KeyError(f"Profile '{profile_name}' not found in configuration.")
        return connections["connections"][profile_name]


def get_connections_params(profile_name: str, session_params: Dict = {}) -> Dict:
    conn_info = get_snowflake_connection_info(profile_name)
    return {
        'user': conn_info["user"],
        'password': conn_info["password"],
        'account': conn_info["account"],
        'session_parameters': session_params
    }


def get_local_snowpark_session(
        profile_name: str,
        session_params: Dict = {},
        snow_park_app_name: str = 'local_developement_app'
    ) -> Session:
    return Session.builder.app_name(snow_park_app_name).configs(
        get_connections_params(profile_name, session_params)
    ).create()