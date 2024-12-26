"""Application constants and metadata pulled directly from the packaged distribution."""

import importlib.metadata

__all__ = ["name", "summary", "version"]

_metadata = importlib.metadata.distribution("auto-rest")

name = _metadata.metadata["name"]
summary = _metadata.metadata["summary"]
version = _metadata.metadata["version"]
