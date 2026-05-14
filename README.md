# 📦Vendor Performance Analysis

A end-to-end data analysis project that explores vendor performance, purchasing behaviour, and profitability insights from an inventory management dataset using Python, SQLite, and data visualisation libraries.

---

## 🗂️ Project Structure

```
├── data/
│   ├── begin_inventory.csv
│   ├── end_inventory.csv
│   ├── purchases.csv
│   ├── purchase_prices.csv
│   ├── sales.csv
│   └── vendor_invoice.csv
├── logs/
│   └── ingestion_db.log
├── inventory.db
├── ingestion_db.ipynb
├── Exploratory_Data_Analysis.ipynb
└── Vendor_Performance_Analysis.ipynb
```

---

## 🔄 Workflow Overview

### 1. `ingestion_db.ipynb` — Data Ingestion
- Reads 6 raw CSV files from the `data/` directory
- Ingests each file into a local **SQLite database** (`inventory.db`) using SQLAlchemy
- Logs ingestion events and total time taken to a log file

### 2. `Exploratory_Data_Analysis.ipynb` — EDA & Feature Engineering
- Connects to `inventory.db` and explores all tables (record counts, schemas, sample rows)
- Investigates relationships between `purchases`, `purchase_prices`, `sales`, and `vendor_invoice` tables
- Builds a consolidated **`vendor_sales_summary`** table using a multi-CTE SQL query joining all relevant tables
- Engineers key business metrics:
  - `GrossProfit` = Total Sales − Total Purchase Cost
  - `ProfitMargin` = (Gross Profit / Total Sales) × 100
  - `StockTurnover` = Total Sales Quantity / Total Purchase Quantity
  - `SalesToPurchaseRatio` = Total Sales Dollars / Total Purchase Dollars
- Handles data quality issues: null values, type casting, whitespace in vendor names
- Stores the final enriched summary table back into SQLite

### 3. `Vendor_Performance_Analysis.ipynb` — Business Insights & Visualisation
Answers key business questions using the `vendor_sales_summary` table:

| Business Question | Analysis Done |
|---|---|
| Which vendors & brands have the highest sales? | Top 10 bar charts for vendors and brands |
| Which vendors contribute most to total purchases? | Pareto chart + Donut chart with cumulative % |
| Do bulk purchases reduce unit price? | Order size segmentation (Small/Medium/Large) + Boxplot |
| Which vendors have slow-moving inventory? | Stock turnover filter (< 1) per vendor |
| How much capital is locked in unsold inventory? | Unsold inventory value aggregation per vendor |
| Which brands have low sales but high margins? | Scatter plot with threshold quadrant analysis |
| Do top vendors have better profit margins? | 95% Confidence Interval comparison (t-distribution) |

---

## 📊 Key Findings

- **Top vendors** dominate total purchase contribution — Pareto analysis reveals that a small number of vendors account for the bulk of procurement spend
- **Bulk purchasing** shows a measurable reduction in unit purchase price across order size segments
- Several vendors have **Stock Turnover < 1**, indicating excess/slow-moving inventory and potential overordering
- Identified a set of **high-margin, low-sales brands** that are strong candidates for targeted promotions or pricing adjustments
- **Confidence interval analysis** shows statistically distinguishable profit margin distributions between top-performing and low-performing vendors

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3.12` | Core language |
| `Pandas` | Data manipulation |
| `NumPy` | Numerical operations |
| `SQLite3 / SQLAlchemy` | Database storage and querying |
| `Matplotlib / Seaborn` | Data visualisation |
| `SciPy` | Statistical analysis (t-test, confidence intervals) |

---

## ⚙️ How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/inventory-vendor-analysis.git
   cd inventory-vendor-analysis
   ```

2. **Install dependencies**
   ```bash
   pip install pandas numpy matplotlib seaborn scipy sqlalchemy
   ```

3. **Run notebooks in order**
   ```
   1. ingestion_db.ipynb           ← Ingest CSVs into SQLite
   2. Exploratory_Data_Analysis.ipynb  ← EDA + build summary table
   3. Vendor_Performance_Analysis.ipynb ← Business insights & charts
   ```

> Make sure the `data/` folder contains all 6 CSV files before running the ingestion notebook.

---

## 📁 Dataset

The dataset contains transactional records from an inventory management system including:
- Beginning and ending inventory levels
- Purchase records and purchase prices
- Sales transactions
- Vendor invoices with freight costs
