import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

__all__ = ["create_app", "run_app"]


def create_app(app_title: str, app_version: str, enable_docs: bool) -> FastAPI:
    """Create and configure a FastAPI application instance.

    This function initializes a FastAPI app with a customizable title, version,
    and optional documentation routes. It also configures application middleware
    for CORS policies.

    Args:
        app_title: The title of the FastAPI application.
        app_version: The version of the FastAPI application.
        enable_docs: Whether to enable the `/docs/` endpoint.

    Returns:
        FastAPI: A configured FastAPI application instance.
    """

    app = FastAPI(
        title=app_title,
        version=app_version,
        docs_url="/docs/" if enable_docs else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
    )

    return app


def run_app(app: FastAPI, server_host: str, server_port: int) -> None:
    """Deploy a FastAPI application server.

    Args:
        app: The FastAPI application to run.
        server_host: The hostname or IP address for the server to bind to.
        server_port: The port number for the server to listen on.
    """

    uvicorn.run(app, host=server_host, port=server_port, log_level="error")
