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

url_num = (
    "https://files.consumerfinance.gov/data/"
    "consumer-credit-trends/mortgages/num_data_MTG.csv"
)

url_volume = (
    "https://files.consumerfinance.gov/data/"
    "consumer-credit-trends/mortgages/vol_data_MTG.csv"
)


# ============================================================
# 2. READ CFPB DATA
# ============================================================

df_30_89 = pd.read_csv(url_30_89)
df_90_plus = pd.read_csv(url_90_plus)

df_num = pd.read_csv(url_num)
df_volume = pd.read_csv(url_volume)


# ============================================================
# 3. TRANSFORM DPD DATA
# ============================================================

id_columns = ["RegionType", "Name", "FIPSCode"]

date_columns = [
    col for col in df_30_89.columns
    if col not in id_columns
]

df_30_89 = df_30_89.melt(
    id_vars=id_columns,
    value_vars=date_columns,
    var_name="Date",
    value_name="DPD_30_89"
)

df_90_plus = df_90_plus.melt(
    id_vars=id_columns,
    value_vars=date_columns,
    var_name="Date",
    value_name="DPD_90_PLUS"
)

df_30_89["Date"] = pd.to_datetime(
    df_30_89["Date"],
    format="%Y-%m"
)

df_90_plus["Date"] = pd.to_datetime(
    df_90_plus["Date"],
    format="%Y-%m"
)


# ============================================================
# 4. MERGE DPD DATA
# ============================================================

merge_columns = [
    "RegionType",
    "Name",
    "FIPSCode",
    "Date"
]

df_dpd = pd.merge(
    df_30_89,
    df_90_plus,
    on=merge_columns,
    how="inner"
)


# ============================================================
# 5. KEEP NATIONAL DPD ONLY
# ============================================================

df_dpd_national = df_dpd[
    df_dpd["RegionType"] == "National"
].copy()


# ============================================================
# 6. PREPARE ORIGINATION DATA
# ============================================================

df_num["Date"] = pd.to_datetime(
    df_num["date"],
    format="%Y-%m"
)

df_volume["Date"] = pd.to_datetime(
    df_volume["date"],
    format="%Y-%m"
)


df_originations = df_num[
    ["Date", "num"]
].rename(
    columns={
        "num": "Originations"
    }
)


df_volume_clean = df_volume[
    ["Date", "vol"]
].rename(
    columns={
        "vol": "Origination_Volume"
    }
)


# ============================================================
# 7. MERGE ORIGINATION COUNT + VOLUME
# ============================================================

df_lending = pd.merge(
    df_originations,
    df_volume_clean,
    on="Date",
    how="inner"
)


# ============================================================
# 8. MERGE WITH NATIONAL DPD
# ============================================================

df_national_dpd = df_dpd_national[
    ["Date", "DPD_30_89", "DPD_90_PLUS"]
]

df_monthly = pd.merge(
    df_lending,
    df_national_dpd,
    on="Date",
    how="inner"
)


# ============================================================
# 9. SORT
# ============================================================

df_monthly = df_monthly.sort_values(
    "Date"
).reset_index(drop=True)


# ============================================================
# 10. DISPLAY
# ============================================================

print("\nFinal monthly dataset shape:")
print(df_monthly.shape)

print("\nColumns:")
print(df_monthly.columns.tolist())

print("\nFirst 10 rows:")
print(df_monthly.head(10))

print("\nLast 10 rows:")
print(df_monthly.tail(10))

print("\nMissing values:")
print(df_monthly.isna().sum())

print("\nDate range:")
print(df_monthly["Date"].min())
print(df_monthly["Date"].max())


# ============================================================
# 11. SAVE
# ============================================================

output_path = "data/monthly_mortgage_risk.csv"

df_monthly.to_csv(
    output_path,
    index=False
)

print("\nSaved to:")
print(output_path)