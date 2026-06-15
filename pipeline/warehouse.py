from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from .config import PROJECT_ROOT


def _sqlite_path(database_url: str) -> Path:
    raw_path = database_url.replace("sqlite:///", "", 1)
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_table(df: pd.DataFrame, table_name: str, database_url: str) -> None:
    if database_url.startswith("sqlite:///"):
        db_path = _sqlite_path(database_url)
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        return

    from sqlalchemy import create_engine

    engine = create_engine(database_url)
    with engine.begin() as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)


def read_table(table_name: str, database_url: str) -> pd.DataFrame:
    if database_url.startswith("sqlite:///"):
        db_path = _sqlite_path(database_url)
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql_query(f"select * from {table_name}", conn)

    from sqlalchemy import create_engine

    engine = create_engine(database_url)
    with engine.begin() as conn:
        return pd.read_sql_query(f"select * from {table_name}", conn)


def describe_database(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return str(_sqlite_path(database_url))
    parsed = urlparse(database_url)
    return f"{parsed.scheme}://{parsed.hostname}:{parsed.port or ''}{parsed.path}"

