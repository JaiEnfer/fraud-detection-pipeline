![CI](https://github.com/JaiEnfer/fraud-detection-pipeline/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Kafka](https://img.shields.io/badge/Streaming-Kafka-orange)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Docker](https://img.shields.io/badge/Containerized-Docker-2496ED)
![License](https://img.shields.io/badge/License-MIT-green)
![Lint](https://img.shields.io/badge/Lint-Ruff-purple)
![Tests](https://img.shields.io/badge/Tests-Pytest-blue)
![API](https://img.shields.io/badge/API-REST-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Event--Driven-black)


# 🚨 Fraud Detection Pipeline (Real-Time, End-to-End)

An end-to-end **real-time fraud detection system** that ingests transactions via API, streams them through Kafka, scores them with a fraud model, and stores predictions in a database.

This project demonstrates **ML + Backend + Streaming + DevOps** in a single production-style architecture.

---

## 🧠 What This System Does

1. A client sends a **transaction** to the API  
2. The API stores the event and **publishes it to Kafka**  
3. A **worker service** consumes the event  
4. A fraud scoring model evaluates the transaction  
5. The prediction is stored in **PostgreSQL**

---

## 🏗️ Architecture
```text
Client → FastAPI → PostgreSQL (events)
                 → Kafka topic (transactions.v1)
                         ↓
                   Worker Consumer → Fraud Model → PostgreSQL (predictions)
```


---

## ⚙️ Tech Stack

| Layer | Technology |
|------|------------|
| API | FastAPI |
| Streaming | Redpanda (Kafka-compatible) |
| Worker | Python Kafka Consumer |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| ML Model | Baseline rule-based fraud scorer |
| DevOps | Docker Compose + GitHub Actions CI |
| Linting | Ruff |
| Testing | Pytest |

---

## 📂 Project Structure

```graphql
app/
  api/            # FastAPI routes & schemas
  core/           # Config and DB setup
  models.py       # SQLAlchemy models
  streaming/      # Kafka producer
  ml/             # Fraud scoring logic

worker/
  consumer.py     # Kafka fraud scoring worker

alembic/          # DB migrations
tests/            # Unit & integration tests
docker-compose.yml
```


---

## 🚀 Running Locally (Full Stack)

### 1️⃣ Start all services

```bash
docker compose up -d --build
```

Services started:

[API](http://localhost:8000)

[API Docs](http://localhost:8000/docs)

[Kafka Console UI](http://localhost:8080)

[Postgres](localhost:5433)



### 2️⃣ Send a Test Transaction

```sh
$id = "evt_$(Get-Random)"
Invoke-RestMethod -Method POST "http://127.0.0.1:8000/transactions" `
  -ContentType "application/json" `
  -Body ("{""id"":""$id"",""user_id"":""u1"",""merchant_id"":""m1"",""amount"":950.0,""currency"":""EUR""}")
```

Example response:

```json
{
  "id": "evt_12345",
  "status": "stored"
}
```

### 3️⃣ See Fraud Predictions

```sh
docker exec -it fraud-db psql -U fraud -d fraud \
  -c "SELECT event_id, score, decision, created_at FROM fraud_predictions ORDER BY created_at DESC LIMIT 5;"
```

---

## 🧪 Running Tests

```sh
pytest -q
```

Integration tests automatically prepare the database schema using Alembic.

---

## 🧹 Linting & Formatting

```sh
ruff check . --fix
ruff format .
```

---

## 🔁 CI Pipeline

GitHub Actions automatically runs:

✅ Tests

✅ Linting

✅ Formatting checks

Every push and pull request is validated.

---

## 🧠 Fraud Model (Baseline)

Current model is a simple rule-based scorer:

- Higher amounts → higher fraud score
- Produces:
   - score (0–1)
   - decision (allow, review, block)
   - explanation

Designed to be easily replaced with a real ML model later.


---

## 🛠️ Environment Variables

| Variable	| Purpose |
|-----------|---------|
| DATABASE_URL | Postgres connection string |
| KAFKA_BOOTSTRAP_SERVERS | Kafka broker address |
| KAFKA_TRANSACTIONS_TOPIC | Topic name for events |

---

## 🧩 Future Improvements

1. Replace rule-based model with trained ML model.
2. Add feature store
3. Add model registry
4. Add monitoring & metrics
5. Add dead-letter queue for failed events

---

___Thank You___


