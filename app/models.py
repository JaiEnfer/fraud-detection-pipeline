from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TransactionEvent(Base):
    __tablename__ = "transaction_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # event id (uuid/trace id)
    source: Mapped[str] = mapped_column(String(64), default="api", nullable=False)

    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    merchant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="EUR", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class FraudPrediction(Base):
    __tablename__ = "fraud_predictions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # prediction id (uuid/trace id)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False)

    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0..1 probability-like score
    decision: Mapped[str] = mapped_column(String(16), nullable=False)  # allow/review/block 

    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
