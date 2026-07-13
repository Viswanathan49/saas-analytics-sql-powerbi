-- Monthly churn count by plan_type
CREATE OR REPLACE VIEW vw_monthly_churn_by_plan AS
SELECT
    d.year_month,
    c.plan_type,
    COUNT(*) AS churned_customers
FROM dim_customer c
JOIN dim_date d
    ON c.churn_date IS NOT NULL
   AND c.churn_date >= d.date
   AND c.churn_date < d.date + INTERVAL '1 month'
GROUP BY d.year_month, c.plan_type
ORDER BY d.year_month, c.plan_type;

-- Monthly MRR by plan_type (from fact_revenue)
CREATE OR REPLACE VIEW vw_monthly_mrr_by_plan AS
SELECT
    d.year_month,
    c.plan_type,
    SUM(fr.amount) AS mrr
FROM fact_revenue fr
JOIN dim_customer c ON fr.customer_key = c.customer_key
JOIN dim_date d ON fr.month_key = d.date_key
GROUP BY d.year_month, c.plan_type
ORDER BY d.year_month, c.plan_type;