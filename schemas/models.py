from __future__ import annotations

from typing import List
from pydantic import BaseModel

class ModelInfo(BaseModel):
    """Minimal subset of the OpenAI /models response schema."""

    id: str
    object: str = "model"
    created: int = 0
    owned_by: str


class ModelList(BaseModel):
    """Top-level data wrapper for GET /v1/models."""

    object: str = "list"
    data: List[ModelInfo] 