with source as (
    select * from {{ source('raw', 'raw_customer_behavior') }}
),

renamed as (
    select
        "Customer_ID" as customer_id,
        cast(nullif("Age", '') as integer) as age,
        "Gender" as gender,
        "Country" as country,
        "City" as city,
        cast(nullif("Membership_Years", '') as numeric) as membership_years,
        cast(nullif("Login_Frequency", '') as numeric) as login_frequency,
        cast(nullif("Session_Duration_Avg", '') as numeric) as session_duration_avg,
        cast(nullif("Pages_Per_Session", '') as numeric) as pages_per_session,
        cast(nullif("Cart_Abandonment_Rate", '') as numeric) as cart_abandonment_rate,
        cast(nullif("Total_Purchases", '') as numeric) as total_purchases,
        cast(nullif("Average_Order_Value", '') as numeric) as average_order_value,
        cast(nullif("Days_Since_Last_Purchase", '') as numeric) as days_since_last_purchase,
        cast(nullif("Customer_Service_Calls", '') as numeric) as customer_service_calls,
        cast(nullif("Lifetime_Value", '') as numeric) as lifetime_value,
        cast(nullif("Churned", '') as integer) as churned
    from source
    where nullif("Customer_ID", '') is not null
)

select * from renamed
