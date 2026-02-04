from __future__ import annotations

from pydantic import BaseModel, Field


class PredictIn(BaseModel):
    user_id: str
    merchant_id: str
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


class PredictOut(BaseModel):
    risk_score: float
    decision: str
    model_version: str
    explanation: str
