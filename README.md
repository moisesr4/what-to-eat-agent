# what-to-eat-agent 🍕

> Conversational AI agent that helps you find the best restaurant near you — filtering by distance, rating, free delivery, and live offers.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Airflow](https://img.shields.io/badge/Airflow-2.9-teal)
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
| Orchestration | Apache Airflow 2.9 | Industry standard, DAG-based, runs locally in Docker |
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
│   └── ui/                     # Streamlit app
│       └── app.py
├── services/
│   ├── api/                    # FastAPI backend
│   │   └── main.py
│   ├── agent/                  # LangChain agent + tools
│   │   ├── agent.py
│   │   └── tools/
│   │       ├── search_restaurants.py
│   │       └── compare_options.py
│   └── pipeline/               # Airflow DAGs + tasks
│       ├── dags/
│       │   ├── ingest.py
│       │   ├── validate.py
│       │   └── transform.py
│       └── tasks/
│           ├── fetch_places.py
│           ├── fetch_yelp.py
│           └── load.py
├── packages/
│   └── shared/                 # Shared config, logging, Pydantic models
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_restaurants.sql
│   │   └── marts/
│   │       └── restaurants_enriched.sql
│   └── dbt_project.yml
├── infra/
│   └── gcp/                    # Cloud Run, BigQuery configs
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## Getting started

### Prerequisites

- Python 3.11+
- Docker + Docker Compose
- GCP account with billing enabled (free tier is enough)
- Google Places API key
- Yelp Fusion API key

### 1. Clone the repo

```bash
git clone https://github.com/your-username/what-to-eat-agent.git
cd what-to-eat-agent
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Start local services (Airflow + API + UI)

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Airflow UI | http://localhost:8080 |
| FastAPI docs | http://localhost:8000/docs |
| Streamlit app | http://localhost:8501 |

### 4. Run the ingestion pipeline

Open Airflow UI → trigger `ingest_restaurants` DAG manually, or wait for the daily schedule (08:00 AM).

### 5. Chat with the agent

Open http://localhost:8501 and ask something like:

> *"Find me a sushi place near the Eiffel Tower with more than 4 stars and free delivery"*

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
- [x] Sprint 1 — repo setup + Google Places ingestion
- [ ] Sprint 2 — Airflow DAGs + dbt models
- [ ] Sprint 3 — pgvector embeddings + RAG
- [ ] Sprint 4 — LangChain agent + tools
- [ ] Sprint 5 — FastAPI + Streamlit UI
- [ ] Sprint 6 — Cloud Run deploy + CI/CD + LangSmith

---

## License

MIT — see [LICENSE](./LICENSE) for details.
