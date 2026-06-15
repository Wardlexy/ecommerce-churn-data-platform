# Pipeline Run Summary

- Run timestamp UTC: `2026-06-15T03:21:43+00:00`
- Warehouse: `C:\Users\lexdw\OneDrive\Documents\Portfolio\Data Engineer\warehouse\ecommerce_churn.db`
- Raw rows: `5008`
- Clean rows: `4990`
- Quality checks passed: `10`
- Quality checks failed: `0`

## Quality Checks

| Check | Status | Severity | Detail |
|---|---|---|---|
| raw_rows_present | pass | error | raw rows=5008 |
| clean_rows_present | pass | error | clean rows=4990 |
| row_retention_above_90pct | pass | warning | retained=4990/5008 |
| customer_id_not_null | pass | error | null customer_id=0 |
| customer_id_unique | pass | error | duplicate customer_id=0 |
| churned_binary | pass | error | values=[0, 1] |
| age_in_valid_range | pass | error | min=15, max=75 |
| cart_abandonment_rate_valid | pass | error | expected 0 to 100 percent |
| estimated_revenue_non_negative | pass | error | min=0.0 |
| risk_segments_populated | pass | warning | segments=['High', 'Low', 'Medium'] |
