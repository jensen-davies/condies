import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from config import CRAGS
from data import load_conditions

st.set_page_config(page_title="Condies", layout="wide")

st.markdown("""
<style>
.block-container {
    max-width: 860px !important;
    margin: 0 auto !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Condies")
st.caption("Climbing conditions forecast · Weather via [Open-Meteo](https://open-meteo.com)")

st.markdown("""
<div style="font-size:0.75rem; color:rgba(255,255,255,0.4); line-height:1.6; margin-bottom:1rem; max-width:600px">
Each window (7am–12pm · 12pm–6pm · 6pm–12am) is scored out of 103:
<b style="color:rgba(255,255,255,0.55)">temperature</b> (60 pts, optimal 44–58°F) +
<b style="color:rgba(255,255,255,0.55)">dew point</b> (40 pts, optimal &lt;45°F) +
<b style="color:rgba(255,255,255,0.55)">wind bonus</b> (3 pts, 5–15 mph).
Any precipitation zeroes the window. The daily score is the average of all three windows.
</div>
""", unsafe_allow_html=True)


# ── Data ─────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_conditions(crag_name: str) -> pd.DataFrame:
    return load_conditions(crag_name)


# ── Scoring helpers ───────────────────────────────────────────────────────────

def score_style(score: float) -> tuple[str, str]:
    if score >= 70:
        return "#2ecc71", "rgba(46,204,113,0.1)"
    elif score >= 40:
        return "#f39c12", "rgba(243,156,18,0.1)"
    else:
        return "#e74c3c", "rgba(231,76,60,0.08)"


# ── UI components ─────────────────────────────────────────────────────────────

def window_card(label: str, score: float, min_temp_f: float, avg_temp_f: float, max_temp_f: float, dewpoint_f: float, precip_in: float) -> str:
    color, bg = score_style(score)
    rain = "<br>🌧 Rain" if precip_in > 0 else ""
    return f"""
    <div style="
        flex: 1;
        min-width: 140px;
        background: {bg};
        border: 1px solid {color}55;
        border-radius: 10px;
        padding: 0.75rem 0.5rem;
        text-align: center;
    ">
        <div style="font-size:0.6rem; text-transform:uppercase; letter-spacing:0.09em; color:rgba(255,255,255,0.4); margin-bottom:0.3rem">{label}</div>
        <div style="font-size:2rem; font-weight:800; color:{color}; line-height:1.1">{score:.0f}</div>
        <div style="font-size:0.6rem; font-weight:700; color:{color}; opacity:0.6; margin-bottom:0.4rem">/103</div>
        <div style="font-size:0.65rem; color:rgba(255,255,255,0.5)"><span style="color:rgba(255,255,255,0.3)">L</span> {min_temp_f:.0f}° <span style="color:rgba(255,255,255,0.3)">A</span> {avg_temp_f:.0f}° <span style="color:rgba(255,255,255,0.3)">H</span> {max_temp_f:.0f}°F</div>
        <div style="font-size:0.65rem; color:rgba(255,255,255,0.35)">{dewpoint_f:.0f}° dew pt{rain}</div>
    </div>"""


def render_forecast(df: pd.DataFrame):
    blocks = []
    for i, (_, row) in enumerate(df.iterrows()):
        day_label = pd.to_datetime(row["day"]).strftime("%A, %b %-d")
        overall = row["climbability_score"]
        avg_color, _ = score_style(overall)
        sep = "margin-top:1.1rem; padding-top:1.1rem; border-top:1px solid rgba(255,255,255,0.07);" if i > 0 else ""

        morning   = window_card("Morning",   row["morning_score"],   row["morning_min_temp_f"],   row["morning_avg_temp_f"],   row["morning_max_temp_f"],   row["morning_avg_dewpoint_f"],   row["morning_precip_in"])
        afternoon = window_card("Afternoon", row["afternoon_score"], row["afternoon_min_temp_f"], row["afternoon_avg_temp_f"], row["afternoon_max_temp_f"], row["afternoon_avg_dewpoint_f"], row["afternoon_precip_in"])
        evening   = window_card("Evening",   row["evening_score"],   row["evening_min_temp_f"],   row["evening_avg_temp_f"],   row["evening_max_temp_f"],   row["evening_avg_dewpoint_f"],   row["evening_precip_in"])

        blocks.append(f"""
        <div style="{sep}">
            <div style="display:flex; align-items:baseline; gap:0.6rem; margin-bottom:0.6rem">
                <span style="font-size:0.95rem; font-weight:700">{day_label}</span>
                <span style="font-size:1rem; color:{avg_color}; font-weight:700">{overall:.1f}</span>
            </div>
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap">{morning}{afternoon}{evening}</div>
        </div>""")

    st.markdown("".join(blocks), unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────

selected_crag = st.selectbox("Crag", list(CRAGS.keys()))
df = get_conditions(selected_crag)
render_forecast(df)
