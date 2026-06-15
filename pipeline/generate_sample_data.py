from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_ecommerce_churn_sample(path: Path, rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    path.parent.mkdir(parents=True, exist_ok=True)

    countries = np.array(["Indonesia", "Singapore", "Malaysia", "Philippines", "Thailand"])
    cities = {
        "Indonesia": ["Jakarta", "Bandung", "Surabaya", "Medan"],
        "Singapore": ["Singapore"],
        "Malaysia": ["Kuala Lumpur", "Penang", "Johor Bahru"],
        "Philippines": ["Manila", "Cebu", "Davao"],
        "Thailand": ["Bangkok", "Chiang Mai", "Phuket"],
    }
    genders = np.array(["Female", "Male", "Other"])
    signup_quarters = np.array(["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4", "2025-Q1", "2025-Q2"])

    customer_ids = [f"CUST-{i:06d}" for i in range(1, rows + 1)]
    country_values = rng.choice(countries, size=rows, p=[0.45, 0.12, 0.18, 0.14, 0.11])
    city_values = [rng.choice(cities[country]) for country in country_values]

    age = np.clip(rng.normal(34, 11, rows).round(), 15, 75)
    membership_years = np.clip(rng.gamma(2.4, 1.3, rows), 0.1, 12)
    login_frequency = np.clip(rng.normal(18, 8, rows), 0, 70)
    session_duration = np.clip(rng.normal(14, 6, rows), 1, 60)
    pages_per_session = np.clip(rng.normal(6, 2.5, rows), 1, 20)
    cart_abandonment = np.clip(rng.normal(38, 20, rows), 0, 100)
    total_purchases = np.clip(rng.poisson(8, rows), 0, 80)
    average_order_value = np.clip(rng.lognormal(4.5, 0.55, rows), 8, 700)
    days_since_last_purchase = np.clip(rng.gamma(2.2, 22, rows), 0, 365)
    discount_usage_rate = np.clip(rng.beta(2.2, 3.5, rows) * 100, 0, 100)
    returns_rate = np.clip(rng.beta(1.5, 8, rows) * 100, 0, 100)
    email_open_rate = np.clip(rng.beta(2.8, 2.3, rows) * 100, 0, 100)
    customer_service_calls = np.clip(rng.poisson(1.2, rows), 0, 20)
    social_engagement = np.clip(rng.normal(52, 23, rows), 0, 100)
    mobile_app_usage = np.clip(rng.normal(5, 3, rows), 0, 24)
    payment_method_diversity = np.clip(rng.poisson(2, rows) + 1, 1, 8)
    wishlist_items = np.clip(rng.poisson(5, rows), 0, 60)
    product_reviews = np.clip(rng.poisson(2, rows), 0, 40)
    lifetime_value = total_purchases * average_order_value + rng.normal(70, 35, rows)
    credit_balance = np.clip(rng.lognormal(3.1, 0.9, rows), 0, 1200)

    churn_score = (
        -2.2
        - 0.045 * login_frequency
        - 0.025 * session_duration
        - 0.02 * email_open_rate
        + 0.018 * cart_abandonment
        + 0.012 * days_since_last_purchase
        + 0.18 * customer_service_calls
        + 0.015 * returns_rate
        - 0.0009 * lifetime_value
    )
    churn_probability = 1 / (1 + np.exp(-churn_score))
    churned = rng.binomial(1, np.clip(churn_probability, 0.02, 0.92))

    df = pd.DataFrame(
        {
            "Customer_ID": customer_ids,
            "Age": age,
            "Gender": rng.choice(genders, size=rows, p=[0.49, 0.49, 0.02]),
            "Country": country_values,
            "City": city_values,
            "Membership_Years": membership_years.round(1),
            "Login_Frequency": login_frequency.round(1),
            "Session_Duration_Avg": session_duration.round(1),
            "Pages_Per_Session": pages_per_session.round(2),
            "Cart_Abandonment_Rate": cart_abandonment.round(2),
            "Wishlist_Items": wishlist_items,
            "Total_Purchases": total_purchases,
            "Average_Order_Value": average_order_value.round(2),
            "Days_Since_Last_Purchase": days_since_last_purchase.round().astype(int),
            "Discount_Usage_Rate": discount_usage_rate.round(2),
            "Returns_Rate": returns_rate.round(2),
            "Email_Open_Rate": email_open_rate.round(2),
            "Customer_Service_Calls": customer_service_calls,
            "Product_Reviews_Written": product_reviews,
            "Social_Media_Engagement_Score": social_engagement.round(2),
            "Mobile_App_Usage": mobile_app_usage.round(1),
            "Payment_Method_Diversity": payment_method_diversity,
            "Lifetime_Value": np.clip(lifetime_value, 0, None).round(2),
            "Credit_Balance": credit_balance.round(2),
            "Signup_Quarter": rng.choice(signup_quarters, size=rows),
            "Churned": churned,
        }
    )

    dirty_rows = max(4, rows // 250)
    dirty_index = rng.choice(df.index, size=dirty_rows, replace=False)
    df["Age"] = df["Age"].astype(object)
    df.loc[dirty_index[: dirty_rows // 2], "Age"] = ""
    df.loc[dirty_index[dirty_rows // 2 :], "Cart_Abandonment_Rate"] = 150
    df = pd.concat([df, df.sample(8, random_state=seed)], ignore_index=True)

    df.to_csv(path, index=False)
    return df
