# E-commerce Churn Data Platform

Portfolio-grade data engineering project for customer churn analytics. This project turns the original coursework idea into a reproducible data platform with ingestion, cleaning, warehouse tables, data quality checks, dbt-style modeling, and dashboard-ready marts.

## What This Project Shows

- Batch ingestion from a raw e-commerce customer behavior CSV.
- Data cleaning and validation for customer, engagement, purchase, and churn fields.
- Warehouse loading into SQLite by default, with Postgres support for Docker-based runs.
- Analytics marts for churn risk, customer behavior, and KPI reporting.
- Data quality reporting that can be shared as portfolio evidence.
- Optional orchestration through Airflow and optional BI through Metabase or Streamlit.

## Architecture

```mermaid
flowchart LR
    A["Raw CSV or generated sample data"] --> B["Python ingestion"]
    B --> C["Raw warehouse table"]
    C --> D["Cleaning and validation"]
    D --> E["Staging table"]
    E --> F["Dim and fact tables"]
    F --> G["Churn risk mart"]
    G --> H["BI dashboard"]
    D --> I["Quality report"]
```

## Project Structure

```text
.
|-- pipeline/                 # Runnable Python ETL code
|-- dags/                     # Airflow DAG example
|-- models/                   # dbt models for warehouse transformation
|-- sql/                      # Warehouse schema and example analytics queries
|-- dashboard/                # Streamlit dashboard starter
|-- tests/                    # Transformation and quality tests
|-- data/                     # Raw and processed data outputs
|-- reports/                  # Quality report and run summary outputs
|-- warehouse/                # Local SQLite warehouse output
|-- legacy/                   # Original coursework artifacts
```

## Quickstart

Create a virtual environment, install dependencies, then run the pipeline.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pipeline.run_pipeline
```

The pipeline creates sample data if `data/raw/ecommerce_customer_behavior.csv` does not exist.

Main outputs:

- `warehouse/ecommerce_churn.db`
- `data/processed/customer_behavior_clean.csv`
- `reports/quality_report.json`
- `reports/pipeline_summary.md`

## Docker Option

Start Postgres, Adminer, and Metabase:

```powershell
docker compose up -d postgres adminer metabase
```

Then run the pipeline against Postgres:

```powershell
$env:DATABASE_URL="postgresql+psycopg://churn:churn@localhost:5432/churn_warehouse"
python -m pipeline.run_pipeline
```

Open:

- Adminer: <http://localhost:8080>
- Metabase: <http://localhost:3000>

## Portfolio Story

This project answers a realistic business question:

> Which e-commerce customers are most likely to churn, and what behavioral signals should retention teams monitor?

The data platform produces:

- Clean customer behavior dataset.
- Customer dimension table.
- Behavior fact table.
- Churn risk mart.
- KPI summary table.
- Quality report with row counts, validation checks, and risk segment coverage.

## Tech Stack

- Python
- pandas
- SQLite or Postgres
- SQL
- dbt model definitions
- Airflow DAG example
- Streamlit dashboard starter
- Docker Compose for local warehouse and BI services

## Legacy Coursework

The original coursework files are preserved in `legacy/`:

- `Data Engineering.docx`
- `Copy_of_UTS_DATA_ANALYTICS.ipynb`

