from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Real-Time Fraud Detection API"
    APP_VERSION: str = "0.3.0"

    DATABASE_URL: str = "postgresql+psycopg://fraud:fraud@localhost:5433/fraud"

    # Kafka / Redpanda
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:19092"
    KAFKA_TRANSACTIONS_TOPIC: str = "transactions.v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
