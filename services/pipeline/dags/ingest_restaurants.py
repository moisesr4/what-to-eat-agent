"""
DAG: ingest_restaurants
Sprint 2 — Daily ingestion of restaurant data from Google Places API into BigQuery.

Fetches restaurants from 4 zones in parallel (paris_14, paris_15, meudon,
boulogne_billancourt), then combines all results and stream-inserts them into
BigQuery (raw.restaurants).
"""

import logging
import sys
from datetime import datetime

# /opt/airflow/tasks is mounted but not a Python package, so we add it to
# sys.path before importing the task modules.
sys.path.insert(0, "/opt/airflow/tasks")

from dotenv import load_dotenv  # noqa: E402

from airflow.decorators import dag, task  # noqa: E402

from fetch_places import fetch_restaurants  # noqa: E402
from load_bigquery import load_to_bigquery  # noqa: E402

load_dotenv()

log = logging.getLogger(__name__)


@dag(
    dag_id="ingest_restaurants",
    schedule="0 8 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["ingestion", "google-places", "sprint-2"],
)
def ingest_restaurants():
    """
    Daily pipeline: fetch restaurants from 4 geographic zones via Google Places
    API and load all rows into BigQuery (raw.restaurants).

    Dependency graph:
        fetch_paris_14  ─┐
        fetch_paris_15  ─┤─▶  load_all_zones
        fetch_meudon    ─┤
        fetch_boulogne  ─┘
    """

    @task
    def fetch_paris_14() -> list[dict]:
        """
        Fetch restaurants from Paris 14e arrondissement (Montparnasse / Alésia area).

        Calls the Google Places Nearby Search API with a 1 500 m radius around
        48.8330 N, 2.3322 E. Each returned row carries zone='paris_14',
        stamped internally by fetch_restaurants via _flatten().

        Returns:
            List of flattened restaurant dicts matching the raw.restaurants schema.
        """
        rows = fetch_restaurants("48.8330,2.3322", "paris_14", radius_m=1500)
        log.info("paris_14: fetched %d rows", len(rows))
        return rows

    @task
    def fetch_paris_15() -> list[dict]:
        """
        Fetch restaurants from Paris 15e arrondissement (Vaugirard / Convention area).

        Calls the Google Places Nearby Search API with a 1 500 m radius around
        48.8422 N, 2.2933 E. Each returned row carries zone='paris_15'.

        Returns:
            List of flattened restaurant dicts matching the raw.restaurants schema.
        """
        rows = fetch_restaurants("48.8422,2.2933", "paris_15", radius_m=1500)
        log.info("paris_15: fetched %d rows", len(rows))
        return rows

    @task
    def fetch_meudon() -> list[dict]:
        """
        Fetch restaurants from Meudon (Hauts-de-Seine, south-west of Paris).

        Calls the Google Places Nearby Search API with a 1 500 m radius around
        48.8136 N, 2.2359 E. Each returned row carries zone='meudon'.

        Returns:
            List of flattened restaurant dicts matching the raw.restaurants schema.
        """
        rows = fetch_restaurants("48.8136,2.2359", "meudon", radius_m=1500)
        log.info("meudon: fetched %d rows", len(rows))
        return rows

    @task
    def fetch_boulogne() -> list[dict]:
        """
        Fetch restaurants from Boulogne-Billancourt (Hauts-de-Seine, west of Paris).

        Calls the Google Places Nearby Search API with a 1 500 m radius around
        48.8352 N, 2.2417 E. Each returned row carries zone='boulogne_billancourt'.

        Returns:
            List of flattened restaurant dicts matching the raw.restaurants schema.
        """
        rows = fetch_restaurants("48.8352,2.2417", "boulogne_billancourt", radius_m=1500)
        log.info("boulogne_billancourt: fetched %d rows", len(rows))
        return rows

    @task
    def load_all_zones(
        rows_paris_14: list[dict],
        rows_paris_15: list[dict],
        rows_meudon: list[dict],
        rows_boulogne: list[dict],
    ) -> int:
        """
        Combine rows from all 4 zones and stream-insert them into BigQuery.

        Logs the row count for each zone individually, then the grand total,
        before calling load_to_bigquery(). On success, logs the number of rows
        confirmed inserted and returns that count.

        Args:
            rows_paris_14:  Rows fetched by fetch_paris_14.
            rows_paris_15:  Rows fetched by fetch_paris_15.
            rows_meudon:    Rows fetched by fetch_meudon.
            rows_boulogne:  Rows fetched by fetch_boulogne.

        Returns:
            Total number of rows successfully inserted into BigQuery.
        """
        zone_batches: dict[str, list[dict]] = {
            "paris_14": rows_paris_14,
            "paris_15": rows_paris_15,
            "meudon": rows_meudon,
            "boulogne_billancourt": rows_boulogne,
        }

        all_rows: list[dict] = []
        for zone, rows in zone_batches.items():
            log.info("zone=%-24s  rows=%d", zone, len(rows))
            all_rows.extend(rows)

        log.info("total rows across all zones: %d", len(all_rows))

        inserted = load_to_bigquery(all_rows)
        log.info("BigQuery insert complete — %d rows inserted", inserted)
        return inserted

    p14 = fetch_paris_14()
    p15 = fetch_paris_15()
    meu = fetch_meudon()
    bou = fetch_boulogne()
    load_all_zones(p14, p15, meu, bou)


ingest_restaurants()
