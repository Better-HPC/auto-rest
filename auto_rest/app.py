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

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

__all__ = ["create_app", "run_server"]


def create_app(app_title: str, app_version: str) -> FastAPI:
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def run_server(app: FastAPI, host: str, port: int) -> None: # pragma: no cover
    """Deploy a FastAPI application server.

    Args:
        app: The FastAPI application to run.
        host: The hostname or IP address for the server to bind to.
        port: The port number for the server to listen on.
    """

    uvicorn.run(app, host=host, port=port, log_level="error")
