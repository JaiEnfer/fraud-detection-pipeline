from __future__ import annotations

import math
from datetime import datetime, timezone


def merchant_risk(merchant_id: str) -> int:
    return sum(merchant_id.encode("utf-8")) % 5


def hour_utc() -> int:
    return datetime.now(timezone.utc).hour


def anomaly_to_risk_score(anomaly_score: float) -> float:
    x = -anomaly_score
    return 1.0 / (1.0 + math.exp(-x))
