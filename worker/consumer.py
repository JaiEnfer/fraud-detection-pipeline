from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
from confluent_kafka import Consumer, KafkaError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import SessionLocal


@dataclass(frozen=True)
class LoadedModel:
    pipeline: Any
    meta: dict[str, Any]


def load_model() -> LoadedModel:
    model_path = Path(os.getenv("MODEL_PATH", "models/fraud_model.joblib"))
    meta_path = Path(os.getenv("MODEL_META_PATH", "models/fraud_model.meta.joblib"))

    pipeline = joblib.load(model_path)
    meta = joblib.load(meta_path)

    return LoadedModel(pipeline=pipeline, meta=meta)


def _merchant_risk(merchant_id: str) -> int:
    """
    Placeholder feature engineering.
    Replace with a lookup table / feature store later.
    """
    # Deterministic small hash → 0..4
    return sum(merchant_id.encode("utf-8")) % 5


def _hour_utc() -> int:
    return datetime.now(timezone.utc).hour


def anomaly_to_risk_score(anomaly_score: float) -> float:
    """
    IsolationForest's score_samples: higher = more normal.
    Convert to a 0..1 "risk" score where higher = more suspicious.

    We use a squashed transform so it's stable.
    """
    # invert and squash
    x = -anomaly_score
    return 1.0 / (1.0 + math.exp(-x))


def upsert_prediction(
    db: Session,
    *,
    pred_id: str,
    event_id: str,
    model_version: str,
    score: float,
    decision: str,
    explanation: str,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO fraud_predictions (id, event_id, model_version, score, decision, explanation, created_at)
            VALUES (:id, :event_id, :model_version, :score, :decision, :explanation, :created_at)
            ON CONFLICT (id) DO UPDATE SET
              score = EXCLUDED.score,
              decision = EXCLUDED.decision,
              explanation = EXCLUDED.explanation,
              created_at = EXCLUDED.created_at,
              model_version = EXCLUDED.model_version
            """
        ),
        {
            "id": pred_id,
            "event_id": event_id,
            "model_version": model_version,
            "score": score,
            "decision": decision,
            "explanation": explanation,
            "created_at": datetime.now(timezone.utc),
        },
    )
    db.commit()


def run() -> None:
    model = load_model()
    model_version = str(model.meta.get("model_version", "unknown"))

    print(f"🟢 Fraud worker started (model={model_version})", flush=True)

    consumer = Consumer(
        {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "fraud-detector-v2",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )
    consumer.subscribe([settings.KAFKA_TRANSACTIONS_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise RuntimeError(msg.error())

            event = json.loads(msg.value().decode("utf-8"))
            event_id = event["id"]
            merchant_id = str(event["merchant_id"])
            amount = float(event["amount"])

            # Feature engineering
            X = [[amount, _merchant_risk(merchant_id), _hour_utc()]]

            # IsolationForest pipeline: score_samples (higher = more normal)
            anomaly_score = float(model.pipeline.score_samples(X)[0])
            risk = anomaly_to_risk_score(anomaly_score)

            decision = "fraud" if risk >= 0.7 else "legit"
            explanation = f"iforest_score={anomaly_score:.6f},risk={risk:.3f}"

            print(f"Scored {event_id} -> risk={risk:.3f} decision={decision}", flush=True)

            db: Session = SessionLocal()
            try:
                upsert_prediction(
                    db,
                    pred_id=f"pred_{event_id}",
                    event_id=event_id,
                    model_version=model_version,
                    score=risk,
                    decision=decision,
                    explanation=explanation,
                )
            finally:
                db.close()
    finally:
        consumer.close()


if __name__ == "__main__":
    time.sleep(2)
    run()
