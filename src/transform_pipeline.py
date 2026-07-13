import pandas as pd
from pathlib import Path
from db import get_engine, load_config

# --------- 1. Extract from CSVs ---------

def extract_customers_df():
    cfg = load_config()
    raw_dir = Path(cfg["paths"]["raw_data"])
    return pd.read_csv(raw_dir / "customers.csv")

def extract_subscriptions_df():
    cfg = load_config()
    raw_dir = Path(cfg["paths"]["raw_data"])
    return pd.read_csv(raw_dir / "subscriptions.csv")

def extract_revenue_df():
    cfg = load_config()
    raw_dir = Path(cfg["paths"]["raw_data"])
    return pd.read_csv(raw_dir / "revenue.csv")

# --------- 2. Transform customers -> dim_customer ---------

def build_dim_customer(customers_df: pd.DataFrame) -> pd.DataFrame:
    df = customers_df.copy()
    df["signup_date"] = pd.to_datetime(df["signup_date"])
    df["churn_date"] = pd.to_datetime(df["churn_date"], errors="coerce")
    df["is_churned"] = df["churn_date"].notna().astype(int)

    dim = df[[
        "customer_id",
        "signup_date",
        "plan_type",
        "monthly_fee",
        "acquisition_cost",
        "churn_date",
        "is_churned"
    ]].drop_duplicates()

    return dim

# --------- 3. Transform months -> dim_date ---------

def build_dim_date_from_months(month_series: pd.Series) -> pd.DataFrame:
    months = pd.to_datetime(month_series.unique(), format="%Y-%m")
    dim = pd.DataFrame({"date": months})
    dim["date_key"] = dim["date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["date"].dt.year
    dim["month"] = dim["date"].dt.month
    dim["day"] = dim["date"].dt.day
    dim["year_month"] = dim["date"].dt.to_period("M").astype(str)
    return dim

# --------- 4. Build fact_subscription using DB keys ---------

def build_fact_subscription_with_keys(subs_df, dim_customer_db, dim_date_db):
    df = subs_df.copy()
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")

    # Join with real customer_key from dim_customer in DB
    df = df.merge(dim_customer_db, on="customer_id", how="left")

    # Prepare dim_date map with matching datetime type
    dim_date_map = dim_date_db.copy()
    dim_date_map["date"] = pd.to_datetime(dim_date_map["date"])
    dim_date_map.rename(columns={"date_key": "month_key"}, inplace=True)

    # Join on month/date to get month_key
    df = df.merge(dim_date_map, left_on="month", right_on="date", how="left")

    fact = df[[
        "subscription_id",
        "customer_key",
        "month_key",
        "month",
        "monthly_fee"
    ]]

    return fact

# --------- 5. Build fact_revenue using DB keys ---------

def build_fact_revenue_with_keys(rev_df, dim_customer_db, dim_date_db):
    df = rev_df.copy()
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")

    # Join with real customer_key
    df = df.merge(dim_customer_db, on="customer_id", how="left")

    # Prepare dim_date map
    dim_date_map = dim_date_db.copy()
    dim_date_map["date"] = pd.to_datetime(dim_date_map["date"])
    dim_date_map.rename(columns={"date_key": "month_key"}, inplace=True)

    # Join on month/date to get month_key
    df = df.merge(dim_date_map, left_on="month", right_on="date", how="left")

    fact = df[[
        "subscription_id",
        "customer_key",
        "month_key",
        "month",
        "monthly_fee",
        "revenue_type",
        "amount"
    ]]

    return fact

# --------- 6. Load dim/fact tables into Postgres ---------

def load_dim_and_facts():
    engine = get_engine()

    # 1. Extract from CSVs
    customers_df = extract_customers_df()
    subs_df = extract_subscriptions_df()
    rev_df = extract_revenue_df()

    # 2. Build dimension DataFrames
    dim_customer_df = build_dim_customer(customers_df)
    dim_date_df = build_dim_date_from_months(subs_df["month"])

    # 3. Load dimensions into DB
    dim_customer_df.to_sql("dim_customer", engine, if_exists="append", index=False)
    dim_date_df.to_sql("dim_date", engine, if_exists="append", index=False)

    # 4. Read back dimensions with real keys
    dim_customer_db = pd.read_sql("SELECT customer_key, customer_id FROM dim_customer", engine)
    dim_date_db = pd.read_sql("SELECT date_key, date FROM dim_date", engine)

    # 5. Build facts using DB keys
    fact_subscription_df = build_fact_subscription_with_keys(subs_df, dim_customer_db, dim_date_db)
    fact_revenue_df = build_fact_revenue_with_keys(rev_df, dim_customer_db, dim_date_db)

    # 6. Load facts
    fact_subscription_df.to_sql("fact_subscription", engine, if_exists="append", index=False)
    fact_revenue_df.to_sql("fact_revenue", engine, if_exists="append", index=False)

if __name__ == "__main__":
    load_dim_and_facts()
