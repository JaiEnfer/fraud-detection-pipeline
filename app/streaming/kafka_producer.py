from __future__ import annotations

import json
from typing import Any

from confluent_kafka import Producer

from app.core.config import settings

_producer: Producer | None = None


def get_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                # best effort durability for dev; tune later
                "acks": "all",
                "retries": 5,
                "linger.ms": 5,
            }
        )
    return _producer


def send_transaction_event(event_id: str, payload: dict[str, Any]) -> None:
    p = get_producer()

    err_holder = {"err": None}

    def delivery_report(err, msg):
        if err is not None:
            err_holder["err"] = err

    p.produce(
        topic=settings.KAFKA_TRANSACTIONS_TOPIC,
        key=event_id.encode("utf-8"),
        value=json.dumps(payload).encode("utf-8"),
        callback=delivery_report,
    )
    p.flush(5)

    if err_holder["err"] is not None:
        raise RuntimeError(f"Kafka delivery failed: {err_holder['err']}")
