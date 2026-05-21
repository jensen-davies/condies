import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()

PROJECT_ID = "condies-497005"
TABLE      = f"`{PROJECT_ID}.marts.fct_conditions`"


@st.cache_resource
def _get_client() -> bigquery.Client:
    # Streamlit Cloud: credentials come from st.secrets
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
        return bigquery.Client(credentials=creds, project=PROJECT_ID)

    # Local dev: GOOGLE_APPLICATION_CREDENTIALS env var points to the JSON keyfile
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path:
        return bigquery.Client.from_service_account_json(key_path)

    return bigquery.Client(project=PROJECT_ID)


@st.cache_data(ttl=3600)
def load_all_conditions() -> dict[str, pd.DataFrame]:
    client = _get_client()

    # QUALIFY is Snowflake-only; use a subquery with window function + WHERE instead
    query = f"""
        SELECT * EXCEPT (latest_fetch_date)
        FROM (
            SELECT
                crag_name,
                day,
                morning_min_temp_f,
                morning_avg_temp_f,
                morning_max_temp_f,
                morning_avg_dewpoint_f,
                morning_precip_in,
                morning_score,
                afternoon_min_temp_f,
                afternoon_avg_temp_f,
                afternoon_max_temp_f,
                afternoon_avg_dewpoint_f,
                afternoon_precip_in,
                afternoon_score,
                evening_min_temp_f,
                evening_avg_temp_f,
                evening_max_temp_f,
                evening_avg_dewpoint_f,
                evening_precip_in,
                evening_score,
                climbability_score,
                MAX(fetch_date) OVER (PARTITION BY crag_name) AS latest_fetch_date,
                fetch_date
            FROM {TABLE}
        )
        WHERE fetch_date = latest_fetch_date
        ORDER BY crag_name, day
    """

    df = client.query(query).to_dataframe()
    return {
        crag: group.drop(columns="crag_name").reset_index(drop=True)
        for crag, group in df.groupby("crag_name")
    }
