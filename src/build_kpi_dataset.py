import pandas as pd

# -----------------------------
# 1. Load master dataset
# -----------------------------
INPUT_FILE = "data/mortgage_master.csv"
OUTPUT_FILE = "data/mortgage_kpi.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])

# Sort chronologically
df = df.sort_values("Date").reset_index(drop=True)


# -----------------------------
# 2. Originations KPIs
# -----------------------------

# Month-over-month change
df["Originations_MoM_Pct"] = (
    df["Originations"].pct_change() * 100
)

# Year-over-year change
df["Originations_YoY_Pct"] = (
    df["Originations"].pct_change(periods=12) * 100
)


# -----------------------------
# 3. Origination Volume KPIs
# -----------------------------

df["Origination_Volume_MoM_Pct"] = (
    df["Origination_Volume"].pct_change() * 100
)

df["Origination_Volume_YoY_Pct"] = (
    df["Origination_Volume"].pct_change(periods=12) * 100
)


# -----------------------------
# 4. Delinquency KPIs
# -----------------------------
# DPD is already expressed as a percentage/rate,
# so changes are represented in percentage points.

df["DPD_30_89_MoM_Ppt"] = (
    df["DPD_30_89"].diff()
)

df["DPD_30_89_YoY_Ppt"] = (
    df["DPD_30_89"].diff(periods=12)
)

df["DPD_90_PLUS_MoM_Ppt"] = (
    df["DPD_90_PLUS"].diff()
)

df["DPD_90_PLUS_YoY_Ppt"] = (
    df["DPD_90_PLUS"].diff(periods=12)
)


# -----------------------------
# 5. Derived Credit Risk KPI
# -----------------------------
# Calculated analytical metric:
# Deep Subprime + Subprime

df["Higher_Risk_Share"] = (
    df["Deep_Subprime_Share"]
    + df["Subprime_Share"]
)

df["Higher_Risk_Share_MoM_Ppt"] = (
    df["Higher_Risk_Share"].diff()
)

df["Higher_Risk_Share_YoY_Ppt"] = (
    df["Higher_Risk_Share"].diff(periods=12)
)


# -----------------------------
# 6. Average mortgage size
# -----------------------------
df["Average_Mortgage_Size"] = (
    df["Origination_Volume"] / df["Originations"]
)


# -----------------------------
# 7. Data quality checks
# -----------------------------

print("\n===== DATA QUALITY CHECK =====")

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Missing values:", df.isna().sum().sum())
print("Duplicate dates:", df["Date"].duplicated().sum())

print(
    "Date range:",
    df["Date"].min().strftime("%Y-%m"),
    "to",
    df["Date"].max().strftime("%Y-%m")
)


# -----------------------------
# 8. Save KPI dataset
# -----------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\nKPI dataset created successfully:")
print(OUTPUT_FILE)

print("\nLast 5 rows:")
print(
    df[
        [
            "Date",
            "Originations",
            "Originations_MoM_Pct",
            "Originations_YoY_Pct",
            "DPD_30_89",
            "DPD_90_PLUS",
            "Higher_Risk_Share",
            "Average_Mortgage_Size",
        ]
    ].tail()
)