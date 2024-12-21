"""Application metadata pulled directly from the packaged distribution."""

import importlib.metadata

__all__ = ["DESCRIPTION", "NAME", "SUMMARY", "VERSION"]

dist = importlib.metadata.distribution("auto-rest")

NAME = dist.metadata["name"]
DESCRIPTION = dist.metadata["description"]
VERSION = dist.metadata["version"]
SUMMARY = dist.metadata["summary"]
