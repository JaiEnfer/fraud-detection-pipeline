from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib


@dataclass(frozen=True)
class LoadedModel:
    pipeline: Any
    meta: dict[str, Any]


_model: LoadedModel | None = None


def load_model() -> LoadedModel:
    global _model
    if _model is not None:
        return _model

    model_path = Path(os.getenv("MODEL_PATH", "models/fraud_model.joblib"))
    meta_path = Path(os.getenv("MODEL_META_PATH", "models/fraud_model.meta.joblib"))

    pipeline = joblib.load(model_path)
    meta = joblib.load(meta_path)

    _model = LoadedModel(pipeline=pipeline, meta=meta)
    return _model
