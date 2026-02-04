from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.predict_schemas import PredictIn, PredictOut
from app.api.schemas import TransactionIn, TransactionOut
from app.core.db import get_db
from app.ml.model_loader import load_model
from app.ml.scoring import anomaly_to_risk_score, hour_utc, merchant_risk
from app.streaming.kafka_producer import send_transaction_event

router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok"}


@router.post("/transactions", response_model=TransactionOut, tags=["transactions"])
def ingest_transaction(payload: TransactionIn, db: Session = Depends(get_db)) -> TransactionOut:
    # Idempotent write: store event once; ignore duplicates
    db.execute(
        text(
            """
            INSERT INTO transaction_events (
              id, source, user_id, merchant_id, amount, currency, created_at
            )
            VALUES (:id, :source, :user_id, :merchant_id, :amount, :currency, now())
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": payload.id,
            "source": "api",
            "user_id": payload.user_id,
            "merchant_id": payload.merchant_id,
            "amount": payload.amount,
            "currency": payload.currency,
        },
    )
    db.commit()

    # Publish to Kafka/Redpanda for downstream real-time scoring
    send_transaction_event(
        event_id=payload.id,
        payload={
            "id": payload.id,
            "user_id": payload.user_id,
            "merchant_id": payload.merchant_id,
            "amount": payload.amount,
            "currency": payload.currency,
        },
    )

    return TransactionOut(id=payload.id, status="stored")


@router.post("/predict", response_model=PredictOut, tags=["model"])
def predict(payload: PredictIn) -> PredictOut:
    model = load_model()
    model_version = str(model.meta.get("model_version", "unknown"))

    X = [[payload.amount, merchant_risk(payload.merchant_id), hour_utc()]]
    anomaly_score = float(model.pipeline.score_samples(X)[0])
    risk = anomaly_to_risk_score(anomaly_score)

    decision = "fraud" if risk >= 0.7 else "legit"
    explanation = f"iforest_score={anomaly_score:.6f},risk={risk:.3f}"

    return PredictOut(
        risk_score=risk,
        decision=decision,
        model_version=model_version,
        explanation=explanation,
    )
