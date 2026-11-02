"""Load and clean the UCI Online Retail dataset."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

def find_source_file():
    candidates = [
        RAW / "Online Retail.xlsx",
        RAW / "online_retail.xlsx",
        RAW / "OnlineRetail.xlsx",
        RAW / "online_retail.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Dataset not found. Download Online Retail.xlsx from UCI and place it in data/raw/."
    )

def load_data(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    # Normalize headers and accommodate common dataset spellings.
    df.columns = [str(c).strip() for c in df.columns]
    required = {"InvoiceNo", "StockCode", "Description", "Quantity",
                "InvoiceDate", "UnitPrice", "CustomerID", "Country"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {sorted(missing)}")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")

    # Remove rows that cannot support customer-attributed sales analysis.
    df = df.dropna(subset=["InvoiceNo", "InvoiceDate", "CustomerID", "Quantity", "UnitPrice"])
    df = df.drop_duplicates()
    # Cancellation invoices commonly start with C; exclude cancellations and non-sales lines.
    df = df[~df["InvoiceNo"].str.upper().str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["CustomerID"] = df["CustomerID"].astype("int64").astype(str)
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["OrderMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["OrderDate"] = df["InvoiceDate"].dt.date.astype(str)
    df["Country"] = df["Country"].fillna("Unknown").astype(str).str.strip()
    df["Description"] = df["Description"].fillna("Unknown").astype(str).str.strip()
    return df.sort_values("InvoiceDate")

def main():
    source = find_source_file()
    raw = load_data(source)
    clean = clean_data(raw)
    out = PROCESSED / "cleaned_retail.csv"
    clean.to_csv(out, index=False)
    print(f"Raw rows: {len(raw):,}")
    print(f"Clean rows: {len(clean):,}")
    print(f"Unique customers: {clean['CustomerID'].nunique():,}")
    print(f"Unique invoices: {clean['InvoiceNo'].nunique():,}")
    print(f"Revenue (dataset currency, GBP): £{clean['Revenue'].sum():,.2f}")
    print(f"Date range: {clean['InvoiceDate'].min()} to {clean['InvoiceDate'].max()}")
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
