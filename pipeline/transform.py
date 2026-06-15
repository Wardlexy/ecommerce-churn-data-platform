from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd


NUMERIC_COLUMNS = [
    "age",
    "membership_years",
    "login_frequency",
    "session_duration_avg",
    "pages_per_session",
    "cart_abandonment_rate",
    "wishlist_items",
    "total_purchases",
    "average_order_value",
    "days_since_last_purchase",
    "discount_usage_rate",
    "returns_rate",
    "email_open_rate",
    "customer_service_calls",
    "product_reviews_written",
    "social_media_engagement_score",
    "mobile_app_usage",
    "payment_method_diversity",
    "lifetime_value",
    "credit_balance",
    "churned",
]

RANGE_LIMITS = {
    "age": (13, 90),
    "membership_years": (0, 20),
    "login_frequency": (0, 1000),
    "session_duration_avg": (0, 1000),
    "pages_per_session": (0, 80),
    "cart_abandonment_rate": (0, 100),
    "wishlist_items": (0, 500),
    "total_purchases": (0, 1000),
    "average_order_value": (0, 10000),
    "days_since_last_purchase": (0, 3650),
    "discount_usage_rate": (0, 100),
    "returns_rate": (0, 100),
    "email_open_rate": (0, 100),
    "customer_service_calls": (0, 100),
    "product_reviews_written": (0, 1000),
    "social_media_engagement_score": (0, 100),
    "mobile_app_usage": (0, 24),
    "payment_method_diversity": (0, 20),
    "lifetime_value": (0, 1_000_000),
    "credit_balance": (0, 100_000),
    "churned": (0, 1),
}


def normalize_column_name(name: str) -> str:
    chars = []
    previous_underscore = False
    for char in name.strip():
        if char.isalnum():
            chars.append(char.lower())
            previous_underscore = False
        elif not previous_underscore:
            chars.append("_")
            previous_underscore = True
    return "".join(chars).strip("_")


def clean_customer_behavior(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"": np.nan, "nan": np.nan, "None": np.nan})

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "customer_id" in df.columns:
        df = df.dropna(subset=["customer_id"])
        df = df.drop_duplicates(subset=["customer_id"], keep="first")
    else:
        df.insert(0, "customer_id", [f"CUST-GENERATED-{i:06d}" for i in range(1, len(df) + 1)])

    if "age" in df.columns:
        low, high = RANGE_LIMITS["age"]
        df.loc[~df["age"].between(low, high), "age"] = np.nan
        df = df.dropna(subset=["age"])

    for col, (low, high) in RANGE_LIMITS.items():
        if col in df.columns and col != "age":
            df.loc[~df[col].between(low, high), col] = np.nan

    for col in df.columns:
        if df[col].isna().sum() == 0:
            continue
        if col in NUMERIC_COLUMNS:
            df[col] = df[col].fillna(df[col].median())
        else:
            mode = df[col].mode(dropna=True)
            df[col] = df[col].fillna(mode.iloc[0] if len(mode) else "Unknown")

    integer_columns = [
        "age",
        "wishlist_items",
        "total_purchases",
        "days_since_last_purchase",
        "customer_service_calls",
        "product_reviews_written",
        "payment_method_diversity",
        "churned",
    ]
    for col in integer_columns:
        if col in df.columns:
            df[col] = df[col].round(0).astype(int)

    for col, (low, high) in RANGE_LIMITS.items():
        if col in df.columns:
            df[col] = df[col].clip(lower=low, upper=high)

    df["estimated_revenue"] = (df["total_purchases"] * df["average_order_value"]).round(2)
    df["engagement_score"] = (
        0.30 * df["login_frequency"].rank(pct=True)
        + 0.25 * df["session_duration_avg"].rank(pct=True)
        + 0.20 * df["pages_per_session"].rank(pct=True)
        + 0.15 * df["email_open_rate"].rank(pct=True)
        + 0.10 * df["mobile_app_usage"].rank(pct=True)
    ).round(4)
    df["churn_risk_score"] = (
        0.30 * df["cart_abandonment_rate"].rank(pct=True)
        + 0.25 * df["days_since_last_purchase"].rank(pct=True)
        + 0.20 * df["customer_service_calls"].rank(pct=True)
        + 0.15 * df["returns_rate"].rank(pct=True)
        + 0.10 * (1 - df["engagement_score"])
    ).round(4)
    df["risk_segment"] = pd.cut(
        df["churn_risk_score"],
        bins=[-0.01, 0.40, 0.70, 1.01],
        labels=["Low", "Medium", "High"],
    ).astype(str)
    df["age_group"] = pd.cut(
        df["age"],
        bins=[12, 24, 34, 44, 54, 90],
        labels=["13-24", "25-34", "35-44", "45-54", "55+"],
    ).astype(str)
    df["load_timestamp_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    ordered_columns = [
        "customer_id",
        "age",
        "age_group",
        "gender",
        "country",
        "city",
        "signup_quarter",
        "membership_years",
        "login_frequency",
        "session_duration_avg",
        "pages_per_session",
        "cart_abandonment_rate",
        "wishlist_items",
        "total_purchases",
        "average_order_value",
        "estimated_revenue",
        "days_since_last_purchase",
        "discount_usage_rate",
        "returns_rate",
        "email_open_rate",
        "customer_service_calls",
        "product_reviews_written",
        "social_media_engagement_score",
        "mobile_app_usage",
        "payment_method_diversity",
        "lifetime_value",
        "credit_balance",
        "engagement_score",
        "churn_risk_score",
        "risk_segment",
        "churned",
        "load_timestamp_utc",
    ]
    return df[[col for col in ordered_columns if col in df.columns]]


def build_warehouse_tables(clean_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    dim_customer = clean_df[
        [
            "customer_id",
            "age",
            "age_group",
            "gender",
            "country",
            "city",
            "signup_quarter",
            "membership_years",
            "load_timestamp_utc",
        ]
    ].copy()

    fact_customer_behavior = clean_df[
        [
            "customer_id",
            "login_frequency",
            "session_duration_avg",
            "pages_per_session",
            "cart_abandonment_rate",
            "wishlist_items",
            "total_purchases",
            "average_order_value",
            "estimated_revenue",
            "days_since_last_purchase",
            "discount_usage_rate",
            "returns_rate",
            "email_open_rate",
            "customer_service_calls",
            "product_reviews_written",
            "social_media_engagement_score",
            "mobile_app_usage",
            "payment_method_diversity",
            "lifetime_value",
            "credit_balance",
            "engagement_score",
            "churn_risk_score",
            "risk_segment",
            "churned",
            "load_timestamp_utc",
        ]
    ].copy()

    mart_churn_risk = clean_df[
        [
            "customer_id",
            "country",
            "city",
            "age_group",
            "engagement_score",
            "churn_risk_score",
            "risk_segment",
            "cart_abandonment_rate",
            "days_since_last_purchase",
            "customer_service_calls",
            "estimated_revenue",
            "lifetime_value",
            "churned",
        ]
    ].copy()

    kpi_summary = pd.DataFrame(
        [
            {
                "customer_count": int(len(clean_df)),
                "churn_rate": round(float(clean_df["churned"].mean()), 4),
                "avg_lifetime_value": round(float(clean_df["lifetime_value"].mean()), 2),
                "avg_estimated_revenue": round(float(clean_df["estimated_revenue"].mean()), 2),
                "high_risk_customers": int((clean_df["risk_segment"] == "High").sum()),
                "medium_risk_customers": int((clean_df["risk_segment"] == "Medium").sum()),
                "low_risk_customers": int((clean_df["risk_segment"] == "Low").sum()),
            }
        ]
    )

    return {
        "stg_customer_behavior": clean_df,
        "dim_customer": dim_customer,
        "fact_customer_behavior": fact_customer_behavior,
        "mart_churn_risk": mart_churn_risk,
        "kpi_summary": kpi_summary,
    }

