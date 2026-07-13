CREATE OR REPLACE VIEW vw_monthly_active_customers AS
SELECT
    d.year_month,
    c.plan_type,
    COUNT(*) AS active_customers
FROM dim_customer c
JOIN dim_date d
    ON c.signup_date < d.date + INTERVAL '1 month'
   AND (c.churn_date IS NULL OR c.churn_date >= d.date)
GROUP BY d.year_month, c.plan_type
ORDER BY d.year_month, c.plan_type;

CREATE OR REPLACE VIEW vw_customer_economics AS
SELECT
customer_id,
plan_type,
monthly_fee,
acquisition_cost,
signup_date,
churn_date,
is_churned,
ROUND(acquisition_cost / NULLIF(monthly_fee, 0), 1) AS cac_payback_months,
CASE WHEN churn_date IS NOT NULL
THEN (churn_date - signup_date)
ELSE NULL END AS tenure_days_at_churn
FROM dim_customer;