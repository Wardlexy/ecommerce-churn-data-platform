from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from .config import load_config
from .generate_sample_data import generate_ecommerce_churn_sample
from .quality import checks_to_records, has_blocking_failures, run_quality_checks
from .transform import build_warehouse_tables, clean_customer_behavior
from .warehouse import describe_database, write_table


def run_pipeline() -> dict[str, object]:
    config = load_config()

    if not config.raw_data_path.exists():
        generate_ecommerce_churn_sample(config.raw_data_path)

    raw_df = pd.read_csv(config.raw_data_path, dtype=str)
    clean_df = clean_customer_behavior(raw_df)
    checks = run_quality_checks(raw_df, clean_df)
    quality_records = checks_to_records(checks)

    config.processed_data_path.parent.mkdir(parents=True, exist_ok=True)
    config.quality_report_path.parent.mkdir(parents=True, exist_ok=True)
    config.summary_report_path.parent.mkdir(parents=True, exist_ok=True)

    clean_df.to_csv(config.processed_data_path, index=False)

    write_table(raw_df, "raw_customer_behavior", config.database_url)
    for table_name, table_df in build_warehouse_tables(clean_df).items():
        write_table(table_df, table_name, config.database_url)
    write_table(pd.DataFrame(quality_records), "pipeline_quality_report", config.database_url)

    report = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "database": describe_database(config.database_url),
        "raw_rows": int(len(raw_df)),
        "clean_rows": int(len(clean_df)),
        "processed_data_path": str(config.processed_data_path),
        "quality_report_path": str(config.quality_report_path),
        "checks": quality_records,
    }

    config.quality_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    config.summary_report_path.write_text(_build_markdown_summary(report), encoding="utf-8")

    if has_blocking_failures(checks):
        failed = [check for check in checks if check.status == "fail" and check.severity == "error"]
        names = ", ".join(check.name for check in failed)
        raise RuntimeError(f"Blocking data quality failures: {names}")

    return report


def _build_markdown_summary(report: dict[str, object]) -> str:
    checks = report["checks"]
    passed = sum(1 for check in checks if check["status"] == "pass")
    failed = len(checks) - passed
    lines = [
        "# Pipeline Run Summary",
        "",
        f"- Run timestamp UTC: `{report['run_timestamp_utc']}`",
        f"- Warehouse: `{report['database']}`",
        f"- Raw rows: `{report['raw_rows']}`",
        f"- Clean rows: `{report['clean_rows']}`",
        f"- Quality checks passed: `{passed}`",
        f"- Quality checks failed: `{failed}`",
        "",
        "## Quality Checks",
        "",
        "| Check | Status | Severity | Detail |",
        "|---|---|---|---|",
    ]
    for check in checks:
        lines.append(f"| {check['name']} | {check['status']} | {check['severity']} | {check['detail']} |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    result = run_pipeline()
    print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2))

