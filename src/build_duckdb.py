import duckdb
import os

# -----------------------------
# File paths
# -----------------------------
DB_FILE = "data/mortgage_risk.duckdb"

MASTER_FILE = "data/mortgage_master.csv"
KPI_FILE = "data/mortgage_kpi.csv"
DPD_FILE = "data/mortgage_dpd_clean.csv"
RISK_FILE = "data/mortgage_risk_profiles.csv"


# -----------------------------
# Create / connect to DuckDB
# -----------------------------
con = duckdb.connect(DB_FILE)

print("Connected to DuckDB")


# -----------------------------
# Load datasets
# -----------------------------

print("\nLoading datasets...")

con.execute("""
    CREATE OR REPLACE VIEW executive_kpis AS

    SELECT
        Date,

        -- Lending metrics
        Originations,
        Origination_Volume,

        -- Delinquency metrics
        DPD_30_89,
        DPD_90_PLUS,

        -- Credit risk composition
        Deep_Subprime_Share,
        Subprime_Share,
        Near_Prime_Share,
        Prime_Share,
        Super_Prime_Share,

        -- Derived risk metric
        Higher_Risk_Share,

        -- Average mortgage size
        Average_Mortgage_Size,

        -- Lending growth
        Originations_MoM_Pct,
        Originations_YoY_Pct,
        Origination_Volume_MoM_Pct,
        Origination_Volume_YoY_Pct,

        -- Delinquency changes
        DPD_30_89_MoM_Ppt,
        DPD_30_89_YoY_Ppt,
        DPD_90_PLUS_MoM_Ppt,
        DPD_90_PLUS_YoY_Ppt,

        -- Risk-share changes
        Higher_Risk_Share_MoM_Ppt,
        Higher_Risk_Share_YoY_Ppt

    FROM mortgage_kpi
""")

# -----------------------------
# Create analytical view
# -----------------------------
# This view will be used later
# by the dashboard / AI analytical tools.

con.execute("""
    CREATE OR REPLACE VIEW executive_kpis AS

    SELECT
        Date,
        Originations,
        Origination_Volume,
        DPD_30_89,
        DPD_90_PLUS,
        Higher_Risk_Share,
        Average_Mortgage_Size,

        Originations_MoM_Pct,
        Originations_YoY_Pct,

        Origination_Volume_MoM_Pct,
        Origination_Volume_YoY_Pct,

        DPD_30_89_MoM_Ppt,
        DPD_30_89_YoY_Ppt,

        DPD_90_PLUS_MoM_Ppt,
        DPD_90_PLUS_YoY_Ppt,

        Higher_Risk_Share_MoM_Ppt,
        Higher_Risk_Share_YoY_Ppt

    FROM mortgage_kpi
""")


# -----------------------------
# Database validation
# -----------------------------

print("\n===== DATABASE VALIDATION =====")

tables = con.execute("""
    SHOW TABLES
""").fetchdf()

print("\nTables:")
print(tables)


print("\nRow counts:")

for table in [
    "mortgage_master",
    "mortgage_kpi",
    "mortgage_dpd",
    "mortgage_risk_profiles"
]:
    count = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count:,} rows")


# -----------------------------
# Test analytical view
# -----------------------------

print("\n===== EXECUTIVE KPI VIEW =====")

result = con.execute("""
    SELECT
        Date,
        Originations,
        Originations_YoY_Pct,
        DPD_30_89,
        DPD_90_PLUS,
        Higher_Risk_Share,
        Average_Mortgage_Size
    FROM executive_kpis
    ORDER BY Date DESC
    LIMIT 5
""").fetchdf()

print(result)


# -----------------------------
# Close connection
# -----------------------------

con.close()

print("\nDuckDB database created successfully:")
print(DB_FILE)