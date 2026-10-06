from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(config_path: str) -> dict[str, Any]:
    config = _read_yaml(Path(config_path))

    # Simple env overrides
    if os.getenv("SOURCE_TYPE"):
        config.setdefault("source", {})["type"] = os.environ["SOURCE_TYPE"]
    if os.getenv("SOURCE_VALUE"):
        config.setdefault("source", {})["value"] = os.environ["SOURCE_VALUE"]
    if os.getenv("MODEL_PATH"):
        config.setdefault("model", {})["path"] = os.environ["MODEL_PATH"]
    if os.getenv("CONFIDENCE"):
        config.setdefault("model", {})["confidence"] = float(os.environ["CONFIDENCE"])
    if os.getenv("SINK_TYPE"):
        config.setdefault("sink", {})["type"] = os.environ["SINK_TYPE"]

    return config