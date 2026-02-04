from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict


class PredictIn(BaseModel):
    
    user_id: str
    merchant_id: str
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


class PredictOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    risk_score: float
    decision: str
    model_version: str
    explanation: str
