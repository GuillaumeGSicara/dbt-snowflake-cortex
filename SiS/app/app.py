
import os
import yaml  # type: ignore
import json
import requests  # type: ignore
import streamlit as st
from snowflake.connector import SnowflakeConnection
from snowflake.snowpark.session import Session
from snowflake.snowpark.context import get_active_session

DATABASE = "DBT_CORTEX"
SCHEMA = "DEFINITIONS"
STAGE = "SEMANTIC_RPT_CUSTOMER_INFORMATIONS"
FILE = "semantic_rpt_customer_informations.yml"


def get_dbt_connection_info(profile_name: str, target_name: str) -> dict[str, str]:
    """Yields a dictionary of the connections from the dbt profiles.yml file in the root user directory.

    Args:
        profile_name (str): The name of the profile in the the profile.yml file.
        target_name (str): the name of the target in the profile.yml file for the profile

    Returns:
        dict[str, str]: a dictionary of the connection information for the profile and target
    """

    profiles_path = os.path.expanduser('~/.dbt/profiles.yml')
    with open(profiles_path, 'r') as file:
        profiles = yaml.safe_load(file)

    return profiles.get(profile_name, {}).get('outputs', {}).get(target_name, {})

def get_connections_params(session_params: dict = {}) -> dict:
    dbt_conn = get_dbt_connection_info(
        profile_name='cortex-profile',
        target_name='dev'
    )
    return {
        'user': dbt_conn["user"],
        'password': dbt_conn["password"],
        'account': dbt_conn["account"],
        'session_parameters': session_params
    }


# For local developement
if 'CONN' not in st.session_state or st.session_state.CONN is None:
    st.session_state.CONN = SnowflakeConnection(**get_connections_params())
    session = session = Session.builder.configs(
        get_connections_params()
    ).create()


def send_message(prompt: str) -> dict:
    """Calls the REST API and returns the response."""
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}",
    }

    resp = requests.post(
        url=f"https://{st.session_state.CONN.host}/api/v2/cortex/analyst/message",
        json=request_body,
        headers={
            "Authorization": f'Snowflake Token="{st.session_state.CONN.rest.token}"',
            "Content-Type": "application/json",
        },
    )

    if resp.status_code < 400:
        return json.loads(resp.content)
    else:
        raise Exception(
            f"Failed request with status {resp.status_code}: {resp.text}"
        )

def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat."""
    st.session_state.messages.append(
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = send_message(prompt=prompt)
            content = response["message"]["content"]
            display_content(content=content)
    st.session_state.messages.append({"role": "assistant", "content": content})


def display_content(content: list, message_index: int = None) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            with st.expander("Suggestions", expanded=True):
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            with st.expander("SQL Query", expanded=False):
                st.code(item["statement"], language="sql")
            with st.expander("Results", expanded=True):
                with st.spinner("Running SQL..."):
                    session = get_active_session()
                    df = session.sql(item["statement"]).to_pandas()
                    if len(df.index) > 1:
                        (data_tab,) = st.tabs(
                            ["Data"]
                        )
                        data_tab.dataframe(df)
                        if len(df.columns) > 1:
                            df = df.set_index(df.columns[0])
                    else:
                        st.dataframe(df)


st.title("Cortex analyst")
st.markdown(f"Semantic Model: `{FILE}`")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = None

for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        display_content(content=message["content"], message_index=message_index)

if user_input := st.chat_input("What is your question?"):
    process_message(prompt=user_input)

if st.session_state.active_suggestion:
    process_message(prompt=st.session_state.active_suggestion)
    st.session_state.active_suggestion = None