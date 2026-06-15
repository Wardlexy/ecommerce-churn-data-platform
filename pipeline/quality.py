from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class QualityCheck:
    name: str
    status: str
    severity: str
    detail: str


def _check(name: str, condition: bool, detail: str, severity: str = "error") -> QualityCheck:
    return QualityCheck(name=name, status="pass" if condition else "fail", severity=severity, detail=detail)


def run_quality_checks(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> list[QualityCheck]:
    checks = [
        _check("raw_rows_present", len(raw_df) > 0, f"raw rows={len(raw_df)}"),
        _check("clean_rows_present", len(clean_df) > 0, f"clean rows={len(clean_df)}"),
        _check(
            "row_retention_above_90pct",
            len(clean_df) >= len(raw_df) * 0.90,
            f"retained={len(clean_df)}/{len(raw_df)}",
            severity="warning",
        ),
        _check(
            "customer_id_not_null",
            clean_df["customer_id"].notna().all(),
            f"null customer_id={clean_df['customer_id'].isna().sum()}",
        ),
        _check(
            "customer_id_unique",
            clean_df["customer_id"].is_unique,
            f"duplicate customer_id={clean_df['customer_id'].duplicated().sum()}",
        ),
        _check(
            "churned_binary",
            set(clean_df["churned"].dropna().unique()).issubset({0, 1}),
            f"values={sorted(clean_df['churned'].dropna().unique().tolist())}",
        ),
        _check(
            "age_in_valid_range",
            clean_df["age"].between(13, 90).all(),
            f"min={clean_df['age'].min()}, max={clean_df['age'].max()}",
        ),
        _check(
            "cart_abandonment_rate_valid",
            clean_df["cart_abandonment_rate"].between(0, 100).all(),
            "expected 0 to 100 percent",
        ),
        _check(
            "estimated_revenue_non_negative",
            (clean_df["estimated_revenue"] >= 0).all(),
            f"min={clean_df['estimated_revenue'].min()}",
        ),
        _check(
            "risk_segments_populated",
            clean_df["risk_segment"].nunique() >= 2,
            f"segments={sorted(clean_df['risk_segment'].dropna().unique().tolist())}",
            severity="warning",
        ),
    ]
    return checks


def checks_to_records(checks: Iterable[QualityCheck]) -> list[dict[str, str]]:
    return [asdict(check) for check in checks]


def has_blocking_failures(checks: Iterable[QualityCheck]) -> bool:
    return any(check.status == "fail" and check.severity == "error" for check in checks)

