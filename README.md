# what-to-eat-agent 🍕

> Conversational AI agent that helps you find the best restaurant near you — filtering by distance, rating, free delivery, and live offers.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Airflow](https://img.shields.io/badge/Airflow-3.2-teal)
![LangChain](https://img.shields.io/badge/LangChain-0.2-purple)
![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What is this?

**what-to-eat-agent** is an end-to-end AI Engineering project that combines a data pipeline with a conversational agent to answer questions like:

> *"Which pizza place near me has free delivery, more than 4 stars, and is open right now?"*

The agent reasons over real restaurant data (Google Places API + Yelp) and responds with ranked recommendations, a map, and contextual explanations — all through a chat interface.

---

## Demo

> 🚧 Coming soon — deploy in progress.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1 · Data sources                                 │
│  Google Places API · Yelp Fusion API · OpenStreetMap    │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2 · Data pipeline · Airflow (Docker)             │
│  DAG ingest → DAG validate → DAG transform (dbt)        │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3 · Storage · GCP                                │
│  BigQuery · Cloud SQL + pgvector · GCS · Firestore      │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 4 · AI Agent · LangChain + Gemini                │
│  Tools: search · filter · compare · recommend           │
│  RAG: semantic context via pgvector embeddings          │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 5 · API + Frontend                               │
│  FastAPI (backend) · Streamlit + Folium (UI + map)      │
│  Deployed on Cloud Run (serverless)                     │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 6 · MLOps & CI/CD                                │
│  GitHub Actions · Docker · LangSmith · Cloud Logging    │
└─────────────────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Orchestration | Apache Airflow 3.2 | Industry standard, DAG-based, runs locally in Docker |
| Transformation | dbt + BigQuery | Modern DE standard, SQL-based, great for portfolios |
| Data validation | Great Expectations | Data quality checks integrated in the pipeline |
| Storage | BigQuery | Scalable, GCP-native, free tier 1TB/month |
| Vector store | Cloud SQL + pgvector | RAG without paying for Pinecone |
| Chat history | Firestore | Serverless, real-time, GCP-native |
| Agent | LangChain | Most adopted agent framework, employable skill |
| LLM | Gemini 1.5 Flash | GCP-native, cost-effective, strong reasoning |
| Backend | FastAPI | Fast, async, auto-generates OpenAPI docs |
| Frontend | Streamlit + Folium | Rapid UI with interactive map, no frontend needed |
| Deploy | Cloud Run | Serverless, scales to zero, free tier friendly |
| CI/CD | GitHub Actions | Automatic lint + test + deploy on push |
| Observability | LangSmith | LLM trace tracking, agent debugging |

---

## Repository structure

```
what-to-eat-agent/
├── apps/
│   └── ui/                     # Streamlit app (Sprint 5)
├── services/
│   ├── api/                    # FastAPI backend (Sprint 5)
│   └── pipeline/               # Airflow DAGs + tasks
│       ├── dags/
│       │   └── ingest_restaurants.py   # Sprint 2: parallel fetch → BigQuery
│       └── tasks/
│           ├── fetch_places.py         # Sprint 1: Google Places Nearby Search
│           └── load_bigquery.py        # Sprint 1: stream-insert to raw.restaurants
├── dbt/                        # dbt models (Sprint 3+)
├── infra/                      # GCP configs (Sprint 6)
├── docker-compose.yml          # Airflow 3.2 stack (api-server, scheduler, triggerer, dag-processor, postgres)
├── Makefile                    # airflow-bootstrap / airflow-up / airflow-down / …
├── .env.example
└── README.md
```

---

## Getting started

### Prerequisites

- Python 3.13+
- Docker Desktop
- GCP account with billing enabled (free tier is enough)
- Google Places API key
- GCP Application Default Credentials configured (`gcloud auth application-default login`)

### 1. Clone the repo

```bash
git clone https://github.com/moisesr4/what-to-eat-agent.git
cd what-to-eat-agent
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. First-time Airflow setup

```bash
make airflow-bootstrap   # runs DB migration + creates admin user + starts all services
```

On subsequent starts:

```bash
make airflow-up
```

| Service | URL | Credentials |
|---|---|---|
| Airflow UI | http://localhost:8080 | admin / admin |

Available Makefile targets:

```
make airflow-up        # start all services in background
make airflow-down      # stop and remove containers
make airflow-restart   # restart without losing volumes
make airflow-logs      # follow logs of all services
make airflow-ps        # show container status
make airflow-shell     # open bash in api-server container
make airflow-clean     # full reset (removes volumes)
```

### 4. Run the ingestion pipeline

Open the Airflow UI → unpause `ingest_restaurants` → trigger manually, or wait for the daily schedule (08:00 UTC).

The DAG fetches restaurants from 4 zones in parallel (Paris 14e, Paris 15e, Meudon, Boulogne-Billancourt) via the Google Places API and stream-inserts them into BigQuery (`raw.restaurants`).

### 5. Chat with the agent

> Coming in Sprint 4 — LangChain agent + tools.

---

## Development

### Running tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Linting

```bash
ruff check .
```

### dbt models

```bash
cd dbt
dbt run --select staging
dbt run --select marts
dbt test
```

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for branch conventions, PR process, and local setup guide for collaborators.

---

## Roadmap

- [x] Project architecture & documentation
- [x] Sprint 1 — repo setup + Google Places ingestion (`fetch_places`, `load_bigquery`)
- [x] Sprint 2 — Airflow 3.2 in Docker + `ingest_restaurants` DAG (4-zone parallel fetch → BigQuery)
- [ ] Sprint 3 — dbt models + data validation
- [ ] Sprint 4 — LangChain agent + tools + pgvector RAG
- [ ] Sprint 5 — FastAPI + Streamlit UI
- [ ] Sprint 6 — Cloud Run deploy + CI/CD + LangSmith

---

## License

MIT — see [LICENSE](./LICENSE) for details.
