from pydantic import BaseModel, Field


class TransactionIn(BaseModel):
    id: str = Field(..., description="Unique event id (e.g. UUID)")
    user_id: str
    merchant_id: str
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", min_length=3, max_length=8)


class TransactionOut(BaseModel):
    id: str
    status: str
