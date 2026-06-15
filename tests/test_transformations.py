from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.generate_sample_data import generate_ecommerce_churn_sample
from pipeline.quality import has_blocking_failures, run_quality_checks
from pipeline.transform import build_warehouse_tables, clean_customer_behavior


def test_clean_customer_behavior_removes_duplicate_ids(tmp_path: Path) -> None:
    raw_path = tmp_path / "sample.csv"
    raw_df = generate_ecommerce_churn_sample(raw_path, rows=500, seed=7)

    clean_df = clean_customer_behavior(pd.read_csv(raw_path, dtype=str))

    assert len(clean_df) <= len(raw_df)
    assert clean_df["customer_id"].is_unique
    assert clean_df["age"].between(13, 90).all()
    assert clean_df["cart_abandonment_rate"].between(0, 100).all()
    assert set(clean_df["churned"].unique()).issubset({0, 1})


def test_quality_checks_have_no_blocking_failures(tmp_path: Path) -> None:
    raw_path = tmp_path / "sample.csv"
    raw_df = generate_ecommerce_churn_sample(raw_path, rows=500, seed=9)
    clean_df = clean_customer_behavior(pd.read_csv(raw_path, dtype=str))
    checks = run_quality_checks(raw_df, clean_df)

    assert not has_blocking_failures(checks)


def test_build_warehouse_tables_returns_expected_marts(tmp_path: Path) -> None:
    raw_path = tmp_path / "sample.csv"
    generate_ecommerce_churn_sample(raw_path, rows=500, seed=11)
    clean_df = clean_customer_behavior(pd.read_csv(raw_path, dtype=str))
    tables = build_warehouse_tables(clean_df)

    assert {"stg_customer_behavior", "dim_customer", "fact_customer_behavior", "mart_churn_risk", "kpi_summary"} <= set(tables)
    assert len(tables["mart_churn_risk"]) == len(clean_df)
    assert int(tables["kpi_summary"].iloc[0]["customer_count"]) == len(clean_df)

