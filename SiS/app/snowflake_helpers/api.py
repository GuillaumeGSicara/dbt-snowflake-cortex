import json
import requests  # type: ignore
from typing import Dict, Any, Optional


def call_snowflake_endpoint(
    method: str,
    endpoint: str,
    env: str,
    host: Optional[str] = None,
    token: Optional[str] = None,
    request_body: Dict[str, Any] = {},
) -> Dict[str, Any]:
    """Calls a Snowflake REST API endpoint based on the environment (prod or local dev).

    Args:
        method (str): Supported REST API method
            (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD).
        endpoint (str): The Snowflake endpoint to call.
        env (str): The environment to run the request in ('prod' or 'dev').
        request_body (Dict[str, Any], optional): Body of the request.
            Defaults to {}.

    Raises:
        ValueError: If the method is not supported.
        Exception: If the request fails.

    Returns:
        Dict[str, Any]: A JSON loaded response from the REST API.
    """
    allowed_methods = {
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
        "HEAD",
    }
    if method.upper() not in allowed_methods:
        raise ValueError(
            f"""HTTP method '{method}' is not allowed.
            Allowed methods are: {allowed_methods}"""
        )

    if env == "prod":
        return _call_snowflake_prod(method, endpoint, request_body)
    elif env == "dev":
        if host is None or token is None:
            raise ValueError(
                "Both 'host' and 'token' must be provided in the 'dev' environment."
            )
        return _call_snowflake_dev(
            method,
            endpoint,
            host,
            token,
            request_body,
        )
    else:
        raise ValueError(f"Environment '{env}' is not recognized. Use 'prod' or 'dev'.")


def _call_snowflake_prod(
    method: str,
    endpoint: str,
    request_body: Dict[str, Any],
) -> Dict[str, Any]:
    """function to call Snowflake endpoint in prod environment."""
    import _snowflake

    resp = _snowflake.send_snow_api_request(
        method.upper(),
        f"{endpoint}",
        {},
        {},
        request_body,
        {},
        30000,
    )
    if resp["status"] < 400:
        return json.loads(resp["content"])
    else:
        raise Exception(f"Failed request with status {resp['status']}: {resp}")


def _call_snowflake_dev(
    method: str,
    endpoint: str,
    host: str,
    token: str,
    request_body: Dict[str, Any],
) -> Dict[str, Any]:
    """Helper function to call Snowflake endpoint in development environment."""
    resp = requests.request(
        method=method.upper(),
        url=f"https://{host}{endpoint}",
        json=request_body,
        headers={
            "Authorization": f'Snowflake Token="{token}"',
            "Content-Type": "application/json",
        },
    )
    if resp.status_code < 400:
        return resp.json()
    else:
        raise Exception(f"Failed request with status {resp.status_code}: {resp.text}")
