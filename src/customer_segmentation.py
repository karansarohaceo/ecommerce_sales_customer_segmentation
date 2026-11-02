"""Build customer RFM features and segment customers with K-Means."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "cleaned_retail.csv"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
REPORTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid")

def main():
    if not DATA.exists():
        raise FileNotFoundError("Run `python -m src.clean_data` first.")
    df = pd.read_csv(DATA, parse_dates=["InvoiceDate"])
    # Snapshot date is one day after the latest transaction, avoiding zero recency.
    snapshot_date = df["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max().normalize()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()

    # RFM values are highly skewed; log1p reduces skew before standardization.
    features = rfm[["Recency", "Frequency", "Monetary"]].copy()
    features["Recency"] = np.log1p(features["Recency"])
    features["Frequency"] = np.log1p(features["Frequency"])
    features["Monetary"] = np.log1p(features["Monetary"].clip(lower=0))
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    # Compare a small range of k values using silhouette score.
    scores = []
    candidate_ks = range(2, 7)
    for k in candidate_ks:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        scores.append({"k": k, "silhouette_score": silhouette_score(X, labels)})
    score_df = pd.DataFrame(scores)
    score_df.to_csv(REPORTS / "cluster_evaluation.csv", index=False)
    best_k = int(score_df.loc[score_df["silhouette_score"].idxmax(), "k"])

    model = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    rfm["Cluster"] = model.fit_predict(X)

    # Descriptive labels are assigned by relative cluster characteristics, not hard-coded cluster IDs.
    summary = rfm.groupby("Cluster").agg(
        Customers=("CustomerID", "nunique"),
        AvgRecencyDays=("Recency", "mean"),
        AvgOrders=("Frequency", "mean"),
        AvgCustomerRevenue=("Monetary", "mean"),
        TotalRevenue=("Monetary", "sum"),
    ).reset_index()
    summary["CustomerSharePct"] = summary["Customers"] / summary["Customers"].sum() * 100
    summary["RevenueSharePct"] = summary["TotalRevenue"] / summary["TotalRevenue"].sum() * 100

    # Heuristic business labels for easier interpretation; verify against the summary.
    recency_mid = summary["AvgRecencyDays"].median()
    freq_mid = summary["AvgOrders"].median()
    mon_mid = summary["AvgCustomerRevenue"].median()
    def label(row):
        if row["AvgRecencyDays"] <= recency_mid and row["AvgOrders"] >= freq_mid and row["AvgCustomerRevenue"] >= mon_mid:
            return "High-value active"
        if row["AvgRecencyDays"] > recency_mid and row["AvgOrders"] >= freq_mid:
            return "At-risk repeat"
        if row["AvgRecencyDays"] <= recency_mid and row["AvgOrders"] < freq_mid:
            return "Recent / developing"
        return "Low-engagement"
    labels = {int(row["Cluster"]): label(row) for _, row in summary.iterrows()}
    rfm["Segment"] = rfm["Cluster"].map(labels)
    summary["Segment"] = summary["Cluster"].map(labels)

    rfm.to_csv(REPORTS / "customer_rfm_segments.csv", index=False)
    summary.to_csv(REPORTS / "segment_summary.csv", index=False)

    # RFM cluster visualization: Frequency vs Monetary, with log scales for readability.
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=rfm, x="Frequency", y="Monetary", hue="Segment", palette="tab10", alpha=0.75)
    plt.xscale("log")
    plt.yscale("log")
    plt.title(f"Customer Segments (K-Means, k={best_k})")
    plt.xlabel("Number of unique invoices (log scale)")
    plt.ylabel("Customer revenue (£, log scale)")
    plt.tight_layout()
    plt.savefig(FIGURES / "customer_segments.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    plot_data = summary.sort_values("TotalRevenue", ascending=False)
    sns.barplot(data=plot_data, x="Segment", y="TotalRevenue")
    plt.title("Revenue by Customer Segment")
    plt.xlabel("Customer segment")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES / "segment_revenue.png", dpi=160)
    plt.close()

    print(f"Selected k: {best_k}")
    print(score_df.to_string(index=False))
    print(summary.to_string(index=False))
    print("Customer segmentation complete. See reports/ and reports/figures/.")

if __name__ == "__main__":
    main()
