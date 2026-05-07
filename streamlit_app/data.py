import pandas as pd
import snowflake.connector
import streamlit as st


def _get_connection():
    s = st.secrets["snowflake"]
    return snowflake.connector.connect(
        account=s["account"],
        user=s["user"],
        password=s["password"],
        database=s["database"],
        warehouse=s["warehouse"],
        schema="MARTS",
    )


def load_all_conditions() -> dict[str, pd.DataFrame]:
    conn = _get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
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
                climbability_score
            FROM fct_conditions
            QUALIFY fetch_date = MAX(fetch_date) OVER (PARTITION BY crag_name)
            ORDER BY crag_name, day
            """
        )
        columns = [desc[0].lower() for desc in cur.description]
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        return {crag: group.drop(columns="crag_name").reset_index(drop=True)
                for crag, group in df.groupby("crag_name")}
    finally:
        cur.close()
        conn.close()
