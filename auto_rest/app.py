"""
The `app` module provides factory functions and utilities for building and
deploying Fast-API applications.


!!! example "Example: Build and Deploy an API"

    ```python
    from auto_rest.app import create_app, run_server

    app = create_app(app_title="My Application", app_version="1.2.3")
    ... # Add endpoints to the application here
    run_server(app, host="127.0.0.1", port=8081)
    ```
"""

import logging
from http import HTTPStatus

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from starlette.responses import Response

__all__ = ["create_rest_app", "create_combined_app", "run_server"]

access_logger = logging.getLogger("auto_rest.access")


async def logging_middleware(request: Request, call_next: callable) -> Response:
    """FastAPI middleware for logging response status codes.

    Args:
        request: The incoming HTTP request.
        call_next: The next middleware in the middleware chain.

    Returns:
        The outgoing HTTP response.
    """

    # Extract metadata from the request
    request_meta = {
        "ip": request.client.host,
        "port": request.client.port,
        "method": request.method,
        "endpoint": request.url.path,
    }

    if request.url.query:
        request_meta["endpoint"] += "?" + request.url.query

    # Execute handling logic
    try:
        response = await call_next(request)

    except Exception as exc:
        access_logger.error(str(exc), exc_info=exc, extra=request_meta)
        raise

    # Log the outgoing response
    status = HTTPStatus(response.status_code)
    level = logging.INFO if status < 400 else logging.ERROR
    access_logger.log(level, f"{status} {status.phrase}", extra=request_meta)

    return response


def create_rest_app(app_title: str, app_version: str) -> FastAPI:
    """Create and configure a FastAPI application instance.

    This function initializes a FastAPI app with a customizable title, version,
    and optional documentation routes. It also configures application middleware
    for CORS policies.

    Args:
        app_title: The title of the FastAPI application.
        app_version: The version of the FastAPI application.

    Returns:
        FastAPI: A configured FastAPI application instance.
    """

    app = FastAPI(
        title=app_title,
        version=app_version,
        docs_url="/docs/",
        redoc_url=None,
    )

    app.middleware("http")(logging_middleware)
    app.add_middleware(CorrelationIdMiddleware)

    # CORS is intentionally permissive here. Origin restrictions and credential
    # handling should be enforced at the proxy level, not the application level.
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def create_mcp_server(app: FastAPI, name: str) -> FastMCP:
    """Create a FastMCP server derived from an existing FastAPI application.

    Converts the FastAPI app's OpenAPI specification into a set of MCP tools,
    one per enabled REST endpoint. The resulting server can be mounted back
    into a parent ASGI application via ``FastMCP.http_app()``.

    Args:
        app: The FastAPI REST application to convert.
        name: The name to assign to the MCP server.

    Returns:
        A configured ``FastMCP`` instance ready to be served.
    """

    access_logger.debug("Generating MCP server from FastAPI app.")
    mcp = FastMCP.from_fastapi(app=app, name=name)
    access_logger.debug(f"MCP server '{name}' created.")
    return mcp


def create_combined_app(rest_app: FastAPI, mcp_asgi_app) -> FastAPI:
    """Create a top-level ASGI application that mounts the REST and MCP sub-applications.

    The combiner carries no middleware of its own. Each sub-application manages
    its own middleware stack, which avoids CORS conflicts between FastAPI and
    FastMCP's OAuth routes.

    Args:
        rest_app: The configured FastAPI REST application.
        mcp_asgi_app: The ASGI application returned by ``FastMCP.http_app()``.

    Returns:
        A FastAPI application with both sub-apps mounted.
    """

    combined = FastAPI(docs_url=None, redoc_url=None, lifespan=mcp_asgi_app.lifespan)
    combined.mount("/mcp", mcp_asgi_app)
    combined.mount("/", rest_app)
    return combined


def run_server(app: FastAPI, host: str, port: int) -> None:  # pragma: no cover
    """Deploy a FastAPI application server.

    Args:
        app: The FastAPI application to run.
        host: The hostname or IP address for the server to bind to.
        port: The port number for the server to listen on.
    """

    # Uvicorn overwrites its logging level when run and needs to be manually disabled here.
    uvicorn.run(app, host=host, port=port, log_level=1000)
