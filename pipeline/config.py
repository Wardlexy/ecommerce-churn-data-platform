from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _path_from_env(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@dataclass(frozen=True)
class PipelineConfig:
    database_url: str
    raw_data_path: Path
    processed_data_path: Path
    quality_report_path: Path
    summary_report_path: Path


def load_config() -> PipelineConfig:
    return PipelineConfig(
        database_url=os.getenv("DATABASE_URL", "sqlite:///warehouse/ecommerce_churn.db"),
        raw_data_path=_path_from_env("RAW_DATA_PATH", "data/raw/ecommerce_customer_behavior.csv"),
        processed_data_path=_path_from_env("PROCESSED_DATA_PATH", "data/processed/customer_behavior_clean.csv"),
        quality_report_path=_path_from_env("QUALITY_REPORT_PATH", "reports/quality_report.json"),
        summary_report_path=_path_from_env("SUMMARY_REPORT_PATH", "reports/pipeline_summary.md"),
    )

