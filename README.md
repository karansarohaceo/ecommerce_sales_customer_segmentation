# E-Commerce Sales & Customer Segmentation Analysis

An end-to-end portfolio project using Python, SQL, Pandas, Seaborn, Matplotlib, and Scikit-Learn. It analyzes retail transactions, generates sales reports, calculates customer Recency-Frequency-Monetary (RFM) metrics, and segments customers using K-Means.

## Dataset

Use the **UCI Online Retail** dataset:
- Dataset page: https://archive.ics.uci.edu/dataset/352/online-retail
- Official dataset: 541,909 transaction rows covering 1 December 2010 through 9 December 2011.
- Columns include invoice, stock code, description, quantity, invoice date, unit price, customer ID, and country.
- The data is licensed CC BY 4.0. Cite: Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33

## Project structure

```text
ecommerce_sales_customer_segmentation/
├── data/
│   ├── raw/                  # Put downloaded source dataset here
│   └── processed/            # Generated cleaned CSV
├── reports/
│   └── figures/              # Generated charts
├── sql/
│   ├── schema.sql
│   └── analysis_queries.sql
├── src/
│   ├── clean_data.py
│   ├── sales_analysis.py
│   └── customer_segmentation.py
├── requirements.txt
└── README.md
```

## 1. Setup

Python 3.10+ is recommended. Open a terminal in the project root.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run the commands below in Command Prompt instead:

```bat
.venv\\Scripts\\activate.bat
```

## 2. Download the dataset

Download `Online Retail.xlsx` from the UCI page above. Place it here:

```text
data/raw/Online Retail.xlsx
```

Do not upload the full raw dataset to GitHub unless you have checked repository size and licensing/attribution needs. The project `.gitignore` excludes raw and generated data by default.

## 3. Run the pipeline

From the project root:

```bash
python -m src.clean_data
python -m src.sales_analysis
python -m src.customer_segmentation
```

Generated outputs:
- `data/processed/cleaned_retail.csv`
- `reports/monthly_sales.csv`
- `reports/top_products.csv`
- `reports/country_sales.csv`
- `reports/weekday_sales.csv`
- `reports/cluster_evaluation.csv`
- `reports/customer_rfm_segments.csv`
- `reports/segment_summary.csv`
- `reports/figures/*.png`

## 4. SQL workflow (MySQL 8+)

1. Run `sql/schema.sql` in MySQL Workbench.
2. Load the cleaned CSV into `ecommerce_analytics.order_items` using the Table Data Import Wizard. Match column names and data types; check date parsing.
3. Run queries in `sql/analysis_queries.sql`.

Python creates the cleaned CSV so the same cleaning logic is used for Python analysis and SQL reporting. For a production pipeline, replace manual CSV import with a repeatable loader and add data-quality checks.

## 5. Methodology

### Data cleaning
- Parse dates and numeric fields.
- Remove duplicate rows.
- Exclude invoice IDs beginning with `C` (cancellations).
- Keep positive quantities and prices for the sales analysis.
- Exclude rows without a customer ID for customer-attributed analysis.
- Calculate `Revenue = Quantity × UnitPrice`.

These choices are analytical assumptions. Returns and cancellations are excluded from the gross sales analysis, so this is not a net-sales/returns report.

### Sales analytics
- Revenue by month, country, product, and weekday.
- Distinct invoice count and customer count.
- Average order value (AOV) in SQL.

### RFM segmentation
- **Recency:** days since the customer's latest purchase at the snapshot date.
- **Frequency:** number of distinct invoices.
- **Monetary:** total recorded revenue.
- Apply `log1p` to reduce skew and `StandardScaler` to put RFM dimensions on comparable scales.
- Compare K-Means candidates from k=2 to k=6 using silhouette score, then fit the best-scoring candidate.
- Cluster names are heuristic summaries based on average RFM values. Review the resulting segment summary before interpreting them as business personas.

## 6. How to interpret results

Do not hard-code results into your resume. Run the pipeline and use the generated outputs to report actual values. Ask:
- Which months have the highest revenue?
- Which products and countries contribute the most revenue?
- Which customer segment contributes the largest revenue share?
- How different are segments in average recency, order frequency, and spend?
- Does the silhouette score suggest clusters are well separated? A higher score is generally better, but business usefulness also matters.

The dataset contains historical data from 2010–2011; do not present it as current retail performance.

## 7. Limitations

- This is observational analysis, not a live marketing experiment.
- The dataset has no campaign exposure/conversion outcomes, so it cannot establish that marketing efficiency increased.
- K-Means cluster IDs have no inherent meaning. Segment labels are descriptive heuristics, not ground-truth customer classes.
- The chosen cleaning rules exclude cancellations, returns represented by negative quantities, and unknown customer IDs; report this when discussing results.

## 8. Resume bullet points (edit after running)

Use only claims supported by your own run and outputs. Example:
- Analyzed **[N] cleaned transaction line items** from the UCI Online Retail dataset using Pandas and SQL to identify revenue trends, top products, and geographic performance.
- Engineered customer-level RFM features and applied Scikit-Learn K-Means clustering, comparing candidate cluster counts using silhouette scores.
- Built Matplotlib/Seaborn visualizations and SQL queries to summarize monthly revenue, order behavior, and segment-level customer value.

## 9. Suggested GitHub topics

`python` `sql` `pandas` `scikit-learn` `customer-segmentation` `rfm-analysis` `ecommerce-analytics` `data-analysis`

## License and attribution

This project code is provided for learning and portfolio use. Attribute the source dataset to UCI Machine Learning Repository and review its CC BY 4.0 terms when redistributing the data.
