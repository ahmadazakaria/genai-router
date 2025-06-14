"""Backend routing configuration loader.

Reads the `backends.yaml` file once and caches the content to provide fast
resolution of *model name → backend definition*.  Falls back to the
environment-driven Ollama default if no configuration is found.

This tiny helper keeps routing logic isolated from FastAPI routes and is
covered by unit-tests in ``tests/test_backend_loader.py``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

import yaml

from .settings import get_settings

CONFIG_FILE_NAME = "backends.yaml"


@lru_cache()
def _load_raw_config() -> Dict[str, Any]:
    """Load the backend configuration YAML once and cache it."""
    config_path = Path(__file__).parent / CONFIG_FILE_NAME
    if not config_path.exists():
        # Return empty dict → fallback to default Ollama backend
        return {}

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def resolve_backend(model_name: str) -> Dict[str, Any]:
    """Return backend settings dict for a given model name.

    If no explicit mapping exists, use the `default_backend` entry or fall back
    to the built-in Ollama base URL from environment variables.
    """

    raw_cfg = _load_raw_config()

    if not raw_cfg:
        # No YAML file → single Ollama backend
        return {
            "type": "ollama",
            "base_url": get_settings().ollama_base_url,
        }

    backends: Dict[str, Any] = raw_cfg.get("backends", {})
    default_backend_key: str | None = raw_cfg.get("default_backend")

    backend_key: str | None = raw_cfg.get("routing", {}).get(model_name, default_backend_key)

    if backend_key is None or backend_key not in backends:
        raise ValueError(f"No backend configured for model '{model_name}' and no default backend set")

    return backends[backend_key] 