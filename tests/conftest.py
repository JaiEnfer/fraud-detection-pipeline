from __future__ import annotations

import time
from collections.abc import Generator

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config
from app.core.db import engine


def _is_integration_test(request: pytest.FixtureRequest) -> bool:
    return request.node.get_closest_marker("integration") is not None


def _alembic_config() -> Config:
    return Config("alembic.ini")


def _wait_for_db(timeout_seconds: int = 30) -> None:
    """
    Wait until Postgres accepts connections.
    Helps avoid race conditions on Windows/Docker Desktop.
    """
    deadline = time.time() + timeout_seconds
    last_err: Exception | None = None

    while time.time() < deadline:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            return
        except OperationalError as e:
            last_err = e
            time.sleep(0.5)

    raise RuntimeError(f"Database not ready after {timeout_seconds}s") from last_err


@pytest.fixture(autouse=True)
def db_bootstrap_for_integration_tests(
    request: pytest.FixtureRequest,
) -> Generator[None, None, None]:
    if not _is_integration_test(request):
        yield
        return

    _wait_for_db()

    # Apply migrations
    command.upgrade(_alembic_config(), "head")

    # Ensure app opens fresh connections
    engine.dispose()

    # Clean tables safely (Postgres doesn't support TRUNCATE IF EXISTS)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF to_regclass('public.fraud_predictions') IS NOT NULL THEN
                        EXECUTE 'TRUNCATE TABLE public.fraud_predictions CASCADE';
                    END IF;

                    IF to_regclass('public.transaction_events') IS NOT NULL THEN
                        EXECUTE 'TRUNCATE TABLE public.transaction_events CASCADE';
                    END IF;
                END $$;
                """
            )
        )

    yield
