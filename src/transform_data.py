import pandas as pd


# ============================================================
# 1. CFPB DATA URLS
# ============================================================

url_30_89 = (
    "https://files.consumerfinance.gov/data/mortgage-performance/"
    "downloads/StateMortgagesPercent-30-89DaysLate-thru-2025-12.csv"
)

url_90_plus = (
    "https://files.consumerfinance.gov/data/mortgage-performance/"
    "downloads/StateMortgagesPercent-90-plusDaysLate-thru-2025-12.csv"
)


# ============================================================
# 2. READ DATA
# ============================================================

df_30_89 = pd.read_csv(url_30_89)
df_90_plus = pd.read_csv(url_90_plus)

print("30–89 original shape:", df_30_89.shape)
print("90+ original shape:", df_90_plus.shape)


# ============================================================
# 3. IDENTIFY ID COLUMNS
# ============================================================

id_columns = ["RegionType", "Name", "FIPSCode"]


# ============================================================
# 4. RESHAPE 30–89 DPD
# ============================================================

date_columns_30_89 = [
    column
    for column in df_30_89.columns
    if column not in id_columns
]

df_30_89_long = df_30_89.melt(
    id_vars=id_columns,
    value_vars=date_columns_30_89,
    var_name="Date",
    value_name="DPD_30_89"
)

df_30_89_long["Date"] = pd.to_datetime(
    df_30_89_long["Date"],
    format="%Y-%m"
)


# ============================================================
# 5. RESHAPE 90+ DPD
# ============================================================

date_columns_90_plus = [
    column
    for column in df_90_plus.columns
    if column not in id_columns
]

df_90_plus_long = df_90_plus.melt(
    id_vars=id_columns,
    value_vars=date_columns_90_plus,
    var_name="Date",
    value_name="DPD_90_PLUS"
)

df_90_plus_long["Date"] = pd.to_datetime(
    df_90_plus_long["Date"],
    format="%Y-%m"
)


# ============================================================
# 6. MERGE THE TWO DATASETS
# ============================================================

merge_columns = [
    "RegionType",
    "Name",
    "FIPSCode",
    "Date"
]

df_risk = pd.merge(
    df_30_89_long,
    df_90_plus_long,
    on=merge_columns,
    how="inner"
)


# ============================================================
# 7. SORT THE DATA
# ============================================================

df_risk = df_risk.sort_values(
    by=["RegionType", "Name", "Date"]
).reset_index(drop=True)


# ============================================================
# 8. DISPLAY RESULTS
# ============================================================

print("\nMerged dataset shape:")
print(df_risk.shape)

print("\nMerged columns:")
print(df_risk.columns.tolist())

print("\nFirst 10 rows:")
print(df_risk.head(10))


# ============================================================
# 9. BASIC DATA QUALITY CHECKS
# ============================================================

print("\nMissing values:")
print(df_risk.isna().sum())

print("\nDuplicate records:")
print(
    df_risk.duplicated(
        subset=merge_columns
    ).sum()
)

print("\nDate range:")
print("Minimum:", df_risk["Date"].min())
print("Maximum:", df_risk["Date"].max())

print("\nRegion types:")
print(df_risk["RegionType"].value_counts())

print("\nDPD statistics:")
print(
    df_risk[
        ["DPD_30_89", "DPD_90_PLUS"]
    ].describe()
)

# ============================================================
# 10. SAVE CLEAN DATASET
# ============================================================

output_path = "data/mortgage_dpd_clean.csv"

df_risk.to_csv(
    output_path,
    index=False
)

print("\nClean dataset saved to:")
print(output_path)