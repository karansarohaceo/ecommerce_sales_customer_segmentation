"""Exploratory sales analysis and chart generation."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "cleaned_retail.csv"
FIGURES = ROOT / "reports" / "figures"
REPORTS = ROOT / "reports"
FIGURES.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid")

def main():
    if not DATA.exists():
        raise FileNotFoundError("Run `python -m src.clean_data` first.")
    df = pd.read_csv(DATA, parse_dates=["InvoiceDate"])
    monthly = df.groupby("OrderMonth", as_index=False).agg(
        revenue=("Revenue", "sum"),
        orders=("InvoiceNo", "nunique"),
        customers=("CustomerID", "nunique"),
    )
    monthly.to_csv(REPORTS / "monthly_sales.csv", index=False)

    products = (df.groupby("Description", as_index=False)
                .agg(revenue=("Revenue", "sum"), units=("Quantity", "sum"))
                .sort_values("revenue", ascending=False))
    products.head(15).to_csv(REPORTS / "top_products.csv", index=False)

    countries = (df.groupby("Country", as_index=False)
                 .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"))
                 .sort_values("revenue", ascending=False))
    countries.head(15).to_csv(REPORTS / "country_sales.csv", index=False)

    # Monthly revenue trend
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=monthly, x="OrderMonth", y="revenue", marker="o")
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES / "monthly_revenue.png", dpi=160)
    plt.close()

    # Top products by revenue
    top = products.head(10).sort_values("revenue")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x="revenue", y="Description")
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue (£)")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.savefig(FIGURES / "top_products.png", dpi=160)
    plt.close()

    # Top countries by revenue
    topc = countries.head(10).sort_values("revenue")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=topc, x="revenue", y="Country")
    plt.title("Top 10 Countries by Revenue")
    plt.xlabel("Revenue (£)")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(FIGURES / "country_revenue.png", dpi=160)
    plt.close()

    # Day-of-week pattern
    df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df.groupby("DayOfWeek", as_index=False)["Revenue"].sum()
    dow["DayOfWeek"] = pd.Categorical(dow["DayOfWeek"], categories=order, ordered=True)
    dow = dow.sort_values("DayOfWeek")
    dow.to_csv(REPORTS / "weekday_sales.csv", index=False)
    plt.figure(figsize=(10, 5))
    sns.barplot(data=dow, x="DayOfWeek", y="Revenue")
    plt.title("Revenue by Day of Week")
    plt.xlabel("Day")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.savefig(FIGURES / "weekday_revenue.png", dpi=160)
    plt.close()

    print("Sales analysis complete. See reports/ and reports/figures/.")

if __name__ == "__main__":
    main()
