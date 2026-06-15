with customer_behavior as (
    select * from {{ ref('stg_customer_behavior') }}
),

scored as (
    select
        customer_id,
        country,
        city,
        age,
        login_frequency,
        cart_abandonment_rate,
        days_since_last_purchase,
        customer_service_calls,
        total_purchases * average_order_value as estimated_revenue,
        lifetime_value,
        churned,
        case
            when cart_abandonment_rate >= 70
              or days_since_last_purchase >= 120
              or customer_service_calls >= 5
                then 'High'
            when cart_abandonment_rate >= 45
              or days_since_last_purchase >= 60
              or customer_service_calls >= 3
                then 'Medium'
            else 'Low'
        end as risk_segment
    from customer_behavior
)

select * from scored

