import pandas as pd
import streamlit as st

from typing import Dict, List, Callable
from snowflake.connector import SnowflakeConnection
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.session import Session

from models.snowflake import ContentType, ContentItem, Message, ResponseModel
from snowflake_helpers.api import call_snowflake_endpoint
from snowflake_helpers.local_connection import get_connections_params, get_local_snowpark_session

DATABASE = "DBT_CORTEX"
SCHEMA = "DEFINITIONS"
STAGE = "SEMANTIC_RPT_CUSTOMER_INFORMATIONS"
FILE = "semantic_rpt_customer_informations.yml"
LOCAL_PROFILE_NAME = "DEMO_CORTEX_ACCOUNT_ADMIN"
ENV: str

# For local developement
try:
    import _snowflake  # type: ignore
    ENV = "prod"
    snowpark_session = get_active_session()
except ImportError:
    st.session_state.CONN = SnowflakeConnection(**get_connections_params(profile_name=LOCAL_PROFILE_NAME))
    snowpark_session =  get_local_snowpark_session(profile_name=LOCAL_PROFILE_NAME)
    ENV = "dev"

def send_message(prompt: str) -> ResponseModel:
    """Calls the REST API and returns the response."""
    request_body = {
        "messages": [
            Message(
                role="user",
                content=[
                    ContentItem(
                        type=ContentType.TEXT,
                        text=prompt
                    )
                ]
            ).model_dump()
        ],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}",
    }

    return ResponseModel(
        **call_snowflake_endpoint(
            method="POST",
            endpoint="/api/v2/cortex/analyst/message",
            env=ENV,
            host=st.session_state.CONN.host if hasattr(st.session_state, 'CONN') else None,
            token=st.session_state.CONN.rest.token if hasattr(st.session_state, 'CONN') else None,
            request_body=request_body
        )
    )

def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat."""
    st.session_state.messages.append(
        Message(
            role="user",
            content=[
                ContentItem(
                    type=ContentType.TEXT,
                    text=prompt
                )
            ]
        )
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = send_message(prompt=prompt)
            content = response.message.content
            display_content(content=content)

    st.session_state.messages.append(
        Message(
            role="assistant",
            content=content
        )
    )

def _display_text(text: str) -> None:
    """Displays a text message."""
    st.markdown(text)

def _display_suggestions(suggestions: List[str], message_index: int) -> None:
    """Displays a list of suggestions."""
    with st.expander("Suggestions", expanded=True):
        for suggestion_index, suggestion in enumerate(suggestions):
            if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                st.session_state.active_suggestion = suggestion

def _display_sql(snowpark_session: Session, statement: str) -> None:
    """Displays a SQL query and its results."""
    with st.expander("SQL Query", expanded=False):
        st.code(statement, language="sql")
    with st.expander("Results", expanded=True):
        with st.spinner("Running SQL..."):
            df = _run_sql(snowpark_session, statement)
            if len(df.index) > 1:
                (data_tab,) = st.tabs(
                    ["Data"]
                )
                data_tab.dataframe(df)
                if len(df.columns) > 1:
                    df = df.set_index(df.columns[0])
            else:
                st.dataframe(df)

def _run_sql(snowpark_session: Session, statement: str) -> pd.DataFrame:
    """Runs a SQL query and displays the results."""
    return snowpark_session.sql(statement).to_pandas()

def display_content(content: List[ContentItem], message_index: int = None) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)

    handlers_register: Dict[str, Callable] = {
        ContentType.TEXT: _display_text,
        ContentType.SUGGESTIONS: _display_suggestions,
        ContentType.SQL: _display_sql,
    }

    for content_item in content:
        handler = handlers_register.get(content_item.type)
        if handler:
            if content_item.type == ContentType.TEXT:
                handler(content_item.text)
            elif content_item.type == ContentType.SUGGESTIONS:
                handler(content_item.suggestions, message_index)
            elif content_item.type == ContentType.SQL:
                handler(snowpark_session, content_item.statement)
        else:
            st.warning(f"Unknown content type: {content_item.type}")


st.title("Cortex analyst")
st.markdown(f"""
            **Environment:** `{ENV}`

            **Semantic Model:** `{FILE}`"""
        )

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = ""

for message_index, message in enumerate(st.session_state.messages):
    message: Message  # type: ignore
    with st.chat_message(message.role):
        display_content(content=message.content, message_index=message_index)

if user_input := st.chat_input("What is your question?"):
    process_message(prompt=user_input)

if st.session_state.active_suggestion:
    process_message(prompt=st.session_state.active_suggestion)
    st.session_state.active_suggestion = None