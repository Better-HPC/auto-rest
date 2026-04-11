"""
The `mcp` module provides factory functions for creating and mounting an MCP
server alongside an existing Auto-REST FastAPI application.

!!! example "Example: Adding MCP to a REST Application"

    ```python
    from auto_rest.app import create_rest_app
    from auto_rest.mcp import create_mcp_app, inject_mcp

    rest_app = create_rest_app(app_title="My App", app_version="1.0.0")
    mcp_app  = create_mcp_app(rest_app, name="My App")
    app      = inject_mcp(rest_app, mcp_app)
    ```
"""

from fastapi import FastAPI
from fastmcp import FastMCP

__all__ = ["create_mcp_app", "inject_mcp"]


def create_mcp_app(rest_app: FastAPI, name: str):
    """Create an MCP ASGI sub-application derived from an existing FastAPI application.

    Converts the REST app's OpenAPI specification into a set of MCP tools, one
    per enabled endpoint. All REST endpoints must be fully registered on
    ``rest_app`` before calling this function, as the OpenAPI spec is read at
    call time.

    Args:
        rest_app: The fully configured FastAPI REST application.
        name: The name to assign to the MCP server.

    Returns:
        An ASGI application returned by ``FastMCP.http_app()``.
    """

    mcp = FastMCP.from_fastapi(app=rest_app, name=name)
    return mcp.http_app(path="/")


def inject_mcp(rest_app: FastAPI, mcp_app) -> FastAPI:
    """Mount an MCP sub-application alongside a REST application under a parent app.

    Creates a bare parent FastAPI application and mounts both sub-applications
    as children. Each sub-application manages its own middleware stack, which
    avoids CORS conflicts between FastAPI and FastMCP's OAuth routes.

    Args:
        rest_app: The configured FastAPI REST application.
        mcp_app: The ASGI application returned by ``create_mcp_app``.

    Returns:
        A parent FastAPI application with both sub-applications mounted.
    """

    app = FastAPI(docs_url=None, redoc_url=None, lifespan=mcp_app.lifespan)
    app.mount("/mcp", mcp_app)
    app.mount("/", rest_app)
    return app
