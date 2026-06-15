# Architecture Notes

## Goal

Build a simple but realistic batch data platform for e-commerce churn analytics. The platform starts from raw customer behavior data and produces a dashboard-ready churn mart.

## Layers

1. Raw layer
   - Stores the original CSV exactly as received.
   - Keeps lineage from source to warehouse.

2. Staging layer
   - Normalizes column names.
   - Converts data types.
   - Handles missing, duplicated, invalid, and outlier values.

3. Warehouse layer
   - Splits data into dimension, fact, and mart tables.
   - Supports dashboard queries without re-running notebook logic.

4. Quality layer
   - Checks row retention, primary key uniqueness, valid ranges, binary churn labels, and risk segment coverage.
   - Writes quality results to JSON and warehouse table.

5. Consumption layer
   - Streamlit dashboard starter.
   - Metabase-ready Postgres warehouse.
   - dbt models for production-style SQL transformation.

## Why This Is Stronger Than The Original Coursework

The original notebook mainly proved data cleaning and descriptive analysis. This upgraded version shows the data engineering lifecycle end to end: ingestion, transformation, validation, warehouse loading, orchestration artifact, and BI-ready marts.

