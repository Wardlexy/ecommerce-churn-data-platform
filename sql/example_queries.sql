-- Churn rate by country
select
    country,
    count(*) as customers,
    round(avg(churned) * 100, 2) as churn_rate_pct
from mart_churn_risk
group by country
order by churn_rate_pct desc;

-- Highest value customers with high churn risk
select
    customer_id,
    country,
    city,
    lifetime_value,
    churn_risk_score,
    risk_segment
from mart_churn_risk
where risk_segment = 'High'
order by lifetime_value desc
limit 25;

-- Business KPI summary
select * from kpi_summary;

