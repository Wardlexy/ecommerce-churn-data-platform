from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "warehouse" / "ecommerce_churn.db"


@st.cache_data
def load_data() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("select * from mart_churn_risk", conn)


st.set_page_config(page_title="E-commerce Churn Platform", layout="wide")
st.title("E-commerce Churn Risk Dashboard")

if not DB_PATH.exists():
    st.warning("Run `python -m pipeline.run_pipeline` first to create the local warehouse.")
    st.stop()

df = load_data()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{len(df):,}")
col2.metric("Churn Rate", f"{df['churned'].mean() * 100:.1f}%")
col3.metric("High Risk", f"{(df['risk_segment'] == 'High').sum():,}")
col4.metric("Avg LTV", f"${df['lifetime_value'].mean():,.0f}")

left, right = st.columns(2)
with left:
    st.subheader("Risk Segment Mix")
    st.bar_chart(df["risk_segment"].value_counts())

with right:
    st.subheader("Churn Rate by Country")
    country = df.groupby("country")["churned"].mean().sort_values(ascending=False) * 100
    st.bar_chart(country)

st.subheader("Highest Value High-Risk Customers")
st.dataframe(
    df[df["risk_segment"] == "High"]
    .sort_values("lifetime_value", ascending=False)
    .head(25),
    use_container_width=True,
)

