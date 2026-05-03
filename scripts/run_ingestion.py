"""
Local orchestrator: fetch restaurants from Google Places API and load to BigQuery.
Runs all 4 zones sequentially. No Airflow or Docker required.

Usage:
    python scripts/run_ingestion.py

Prerequisites:
    - GOOGLE_PLACES_API_KEY set in .env
    - GCP_PROJECT_ID set in .env
    - BIGQUERY_DATASET set in .env (defaults to "raw")
    - gcloud auth application-default login (run once)
"""

import sys
import time
from pathlib import Path

# Allow imports from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.pipeline.tasks.fetch_places import fetch_restaurants
from services.pipeline.tasks.load_bigquery import load_to_bigquery

ZONES = [
    ("48.8330,2.3322", "paris_14"),
    ("48.8422,2.2933", "paris_15"),
    ("48.8136,2.2359", "meudon"),
    ("48.8352,2.2417", "boulogne_billancourt"),
]

RADIUS_M = 1000.0
SLEEP_BETWEEN_ZONES = 2  # seconds — avoid hammering the API


def main() -> None:
    total_fetched = 0
    total_loaded = 0

    for lat_lng, zone in ZONES:
        print(f"\n[{zone}] Fetching restaurants at {lat_lng} (radius {RADIUS_M:.0f}m)...")
        try:
            rows = fetch_restaurants(lat_lng, zone, radius_m=RADIUS_M)
            print(f"[{zone}] Fetched {len(rows)} restaurants.")
        except Exception as exc:
            print(f"[{zone}] FETCH ERROR: {exc}")
            continue

        if not rows:
            print(f"[{zone}] No results — skipping load.")
            continue

        print(f"[{zone}] Loading to BigQuery...")
        try:
            loaded = load_to_bigquery(rows)
            print(f"[{zone}] Loaded {loaded} rows.")
            total_fetched += len(rows)
            total_loaded += loaded
        except Exception as exc:
            print(f"[{zone}] LOAD ERROR: {exc}")

        time.sleep(SLEEP_BETWEEN_ZONES)

    print(f"\nDone. Fetched {total_fetched} rows, loaded {total_loaded} rows across {len(ZONES)} zones.")


if __name__ == "__main__":
    main()
