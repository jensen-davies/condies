from dagster import asset, MaterializeResult, MetadataValue

from config import CRAGS
from ingestion.open_meteo import (
    get_client,
    ensure_table,
    fetch_with_backoff,
    insert_row,
    HOURLY_VARS,
    DAILY_VARS,
)


@asset
def raw_weather() -> MaterializeResult:
    client = get_client()
    ensure_table(client)

    for name, coords in CRAGS.items():
        params = {
            "latitude":      coords["lat"],
            "longitude":     coords["lon"],
            "hourly":        HOURLY_VARS,
            "daily":         DAILY_VARS,
            "timezone":      "auto",
            "forecast_days": 3,
        }
        payload = fetch_with_backoff(params)
        insert_row(client, name, coords["lat"], coords["lon"], payload)

    return MaterializeResult(
        metadata={
            "rows_inserted": MetadataValue.int(len(CRAGS)),
            "crags":         MetadataValue.text(", ".join(CRAGS.keys())),
        }
    )
