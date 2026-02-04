from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class ModelMeta:
    model_name: str
    model_version: str
    trained_at_utc: str
    features: list[str]


def main() -> None:
    # Synthetic "normal" transaction data for a baseline anomaly detector.
    # In real life, you’d train on historical legitimate transactions.
    rng = np.random.default_rng(42)
    n = 50_000

    amounts = rng.lognormal(mean=3.2, sigma=0.55, size=n)  # mostly small/moderate
    merchant_risk = rng.integers(0, 5, size=n)             # 0..4 (fake feature)
    hour = rng.integers(0, 24, size=n)                     # 0..23

    X = np.column_stack([amounts, merchant_risk, hour])

    pipe: Pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", IsolationForest(
                n_estimators=200,
                contamination=0.01,
                random_state=42,
            )),
        ]
    )

    pipe.fit(X)

    model_version = "iforest-v1"
    meta = ModelMeta(
        model_name="isolation_forest_baseline",
        model_version=model_version,
        trained_at_utc=datetime.now(timezone.utc).isoformat(),
        features=["amount", "merchant_risk", "hour"],
    )

    out_dir = Path("models")
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipe, out_dir / "fraud_model.joblib")
    joblib.dump(asdict(meta), out_dir / "fraud_model.meta.joblib")

    print(f"Saved model to {out_dir / 'fraud_model.joblib'}")
    print(f"Saved meta  to {out_dir / 'fraud_model.meta.joblib'}")


if __name__ == "__main__":
    main()
