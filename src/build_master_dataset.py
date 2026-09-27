import pandas as pd


# ============================================================
# 1. LOAD EXISTING CLEAN DATA
# ============================================================

df_monthly = pd.read_csv(
    "data/monthly_mortgage_risk.csv"
)

df_risk_profile = pd.read_csv(
    "data/mortgage_risk_profiles.csv"
)


# ============================================================
# 2. CONVERT DATE COLUMNS
# ============================================================

df_monthly["Date"] = pd.to_datetime(
    df_monthly["Date"]
)

df_risk_profile["Date"] = pd.to_datetime(
    df_risk_profile["Date"]
)


# ============================================================
# 3. MERGE
# ============================================================

df_master = pd.merge(
    df_monthly,
    df_risk_profile,
    on="Date",
    how="inner"
)


# ============================================================
# 4. SORT
# ============================================================

df_master = df_master.sort_values(
    "Date"
).reset_index(drop=True)


# ============================================================
# 5. BASIC VALIDATION
# ============================================================

print("Master dataset shape:")
print(df_master.shape)

print("\nColumns:")
print(df_master.columns.tolist())

print("\nDate range:")
print(df_master["Date"].min())
print(df_master["Date"].max())

print("\nMissing values:")
print(df_master.isna().sum())

print("\nDuplicate dates:")
print(df_master["Date"].duplicated().sum())


# ============================================================
# 6. DISPLAY SAMPLE
# ============================================================

print("\nFirst 5 rows:")
print(df_master.head())

print("\nLast 5 rows:")
print(df_master.tail())


# ============================================================
# 7. SAVE MASTER DATASET
# ============================================================

output_path = "data/mortgage_master.csv"

df_master.to_csv(
    output_path,
    index=False
)

print("\nMaster dataset saved to:")
print(output_path)