"""
Load a list of flattened restaurant rows into BigQuery (raw.restaurants).
Creates the dataset and table if they don't exist.

Usage:
    from services.pipeline.tasks.load_bigquery import load_to_bigquery
    load_to_bigquery(rows, project_id="my-project", dataset_id="raw")

Authentication: uses Application Default Credentials.
Run `gcloud auth application-default login` once locally.
"""

import os

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

TABLE_ID = "restaurants"

SCHEMA = [
    bigquery.SchemaField("place_id", "STRING"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("address", "STRING"),
    bigquery.SchemaField("lat", "FLOAT64"),
    bigquery.SchemaField("lng", "FLOAT64"),
    bigquery.SchemaField("rating", "FLOAT64"),
    bigquery.SchemaField("user_rating_count", "INT64"),
    bigquery.SchemaField("price_level", "STRING"),
    bigquery.SchemaField("primary_type", "STRING"),
    bigquery.SchemaField("types", "STRING"),
    bigquery.SchemaField("business_status", "STRING"),
    bigquery.SchemaField("phone_national", "STRING"),
    bigquery.SchemaField("phone_international", "STRING"),
    bigquery.SchemaField("website_uri", "STRING"),
    bigquery.SchemaField("google_maps_uri", "STRING"),
    bigquery.SchemaField("open_now", "BOOL"),
    bigquery.SchemaField("next_close_time", "STRING"),
    bigquery.SchemaField("weekday_descriptions", "STRING"),
    bigquery.SchemaField("takeout", "BOOL"),
    bigquery.SchemaField("delivery", "BOOL"),
    bigquery.SchemaField("dine_in", "BOOL"),
    bigquery.SchemaField("reservable", "BOOL"),
    bigquery.SchemaField("serves_beer", "BOOL"),
    bigquery.SchemaField("serves_wine", "BOOL"),
    bigquery.SchemaField("serves_cocktails", "BOOL"),
    bigquery.SchemaField("outdoor_seating", "BOOL"),
    bigquery.SchemaField("live_music", "BOOL"),
    bigquery.SchemaField("good_for_children", "BOOL"),
    bigquery.SchemaField("good_for_groups", "BOOL"),
    bigquery.SchemaField("accepts_credit_cards", "BOOL"),
    bigquery.SchemaField("accepts_debit_cards", "BOOL"),
    bigquery.SchemaField("accepts_cash_only", "BOOL"),
    bigquery.SchemaField("accepts_nfc", "BOOL"),
    bigquery.SchemaField("free_parking_lot", "BOOL"),
    bigquery.SchemaField("free_street_parking", "BOOL"),
    bigquery.SchemaField("paid_street_parking", "BOOL"),
    bigquery.SchemaField("valet_parking", "BOOL"),
    bigquery.SchemaField("wheelchair_accessible_entrance", "BOOL"),
    bigquery.SchemaField("wheelchair_accessible_restroom", "BOOL"),
    bigquery.SchemaField("wheelchair_accessible_seating", "BOOL"),
    bigquery.SchemaField("photo_count", "INT64"),
    bigquery.SchemaField("zone", "STRING"),
    bigquery.SchemaField("fetched_at", "STRING"),
]


def _ensure_dataset(client: bigquery.Client, dataset_ref: bigquery.DatasetReference) -> None:
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "EU"
    client.create_dataset(dataset, exists_ok=True)


def _ensure_table(client: bigquery.Client, table_ref: bigquery.TableReference) -> None:
    table = bigquery.Table(table_ref, schema=SCHEMA)
    client.create_table(table, exists_ok=True)


def load_to_bigquery(
    rows: list[dict],
    project_id: str | None = None,
    dataset_id: str | None = None,
) -> int:
    """
    Insert rows into BigQuery using streaming inserts.

    Args:
        rows: list of flattened dicts from fetch_restaurants()
        project_id: GCP project ID (falls back to GCP_PROJECT_ID env var)
        dataset_id: BigQuery dataset name (falls back to BIGQUERY_DATASET env var)

    Returns:
        Number of rows successfully inserted.

    Raises:
        RuntimeError: if required env vars are missing or insert errors occur.
    """
    project_id = project_id or os.environ.get("GCP_PROJECT_ID")
    dataset_id = dataset_id or os.environ.get("BIGQUERY_DATASET", "raw")

    if not project_id:
        raise RuntimeError("GCP_PROJECT_ID is not set")
    if not rows:
        print("No rows to insert.")
        return 0

    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(TABLE_ID)

    _ensure_dataset(client, dataset_ref)
    _ensure_table(client, table_ref)

    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")

    return len(rows)
