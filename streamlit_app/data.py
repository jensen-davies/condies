import os

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def _get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema="MARTS",
    )


def load_conditions(crag_name: str) -> pd.DataFrame:
    conn = _get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT
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
            WHERE crag_name = %s
              AND fetch_date = (
                  SELECT MAX(fetch_date) FROM fct_conditions WHERE crag_name = %s
              )
            ORDER BY day
            """,
            (crag_name, crag_name),
        )
        columns = [desc[0].lower() for desc in cur.description]
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=columns)
    finally:
        cur.close()
        conn.close()
