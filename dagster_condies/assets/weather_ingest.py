from dagster import asset, MaterializeResult, MetadataValue

from config import CRAGS
from ingestion.open_meteo import (
    get_connection,
    ensure_table,
    fetch_with_backoff,
    insert_row,
    HOURLY_VARS,
    DAILY_VARS,
)


@asset
def raw_weather() -> MaterializeResult:
    conn = get_connection()
    cur = conn.cursor()
    ensure_table(cur)

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
        insert_row(cur, name, coords["lat"], coords["lon"], payload)

    conn.commit()
    cur.close()
    conn.close()

    return MaterializeResult(
        metadata={
            "rows_inserted": MetadataValue.int(len(CRAGS)),
            "crags":         MetadataValue.text(", ".join(CRAGS.keys())),
        }
    )
