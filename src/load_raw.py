import pandas as pd
from pathlib import Path
from db import get_engine, load_config   # make sure db.py has these

def main():
    # Load config (so paths come from config/config_dev.yaml)
    cfg = load_config()
    raw_dir = Path(cfg["paths"]["raw_data"])

    # 1) Customers
    customers_path = raw_dir / "customers.csv"
    customers_df = pd.read_csv(customers_path)
    engine = get_engine()
    customers_df.to_sql(
        "customers_raw",
        engine,
        if_exists="replace",   # overwrite for now; later you can use "append"
        index=False
    )

    # 2) Subscriptions
    subscriptions_path = raw_dir / "subscriptions.csv"
    subscriptions_df = pd.read_csv(subscriptions_path)
    subscriptions_df.to_sql(
        "subscriptions_raw",
        engine,
        if_exists="replace",
        index=False
    )

    # 3) Revenue
    revenue_path = raw_dir / "revenue.csv"
    revenue_df = pd.read_csv(revenue_path)
    revenue_df.to_sql(
        "revenue_raw",
        engine,
        if_exists="replace",
        index=False
    )

if __name__ == "__main__":
    main()
