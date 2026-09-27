import pandas as pd


# ============================================================
# 1. CFPB RISK PROFILE DATA
# ============================================================

url_risk = (
    "https://files.consumerfinance.gov/data/"
    "consumer-credit-trends/mortgages/"
    "volume_data_Score_Level_MTG.csv"
)


# ============================================================
# 2. READ DATA
# ============================================================

df = pd.read_csv(url_risk)

print("Original shape:", df.shape)


# ============================================================
# 3. CONVERT DATE
# ============================================================

df["Date"] = pd.to_datetime(
    df["date"],
    format="%Y-%m"
)


# ============================================================
# 4. KEEP REQUIRED COLUMNS
# ============================================================

df = df[
    ["Date", "credit_score_group", "vol"]
].copy()


# ============================================================
# 5. PIVOT CREDIT SCORE GROUPS
# ============================================================

df_risk_profile = df.pivot(
    index="Date",
    columns="credit_score_group",
    values="vol"
).reset_index()


# ============================================================
# 6. CLEAN COLUMN NAMES
# ============================================================

df_risk_profile = df_risk_profile.rename(
    columns={
        "Deep subprime": "Deep_Subprime_Volume",
        "Subprime": "Subprime_Volume",
        "Near-prime": "Near_Prime_Volume",
        "Prime": "Prime_Volume",
        "Super-prime": "Super_Prime_Volume"
    }
)


# ============================================================
# 7. CALCULATE TOTAL VOLUME
# ============================================================

risk_columns = [
    "Deep_Subprime_Volume",
    "Subprime_Volume",
    "Near_Prime_Volume",
    "Prime_Volume",
    "Super_Prime_Volume"
]

df_risk_profile["Total_Risk_Profile_Volume"] = (
    df_risk_profile[risk_columns]
    .sum(axis=1)
)


# ============================================================
# 8. CALCULATE RISK MIX %
# ============================================================

for column in risk_columns:

    share_column = column.replace(
        "_Volume",
        "_Share"
    )

    df_risk_profile[share_column] = (
        df_risk_profile[column]
        / df_risk_profile["Total_Risk_Profile_Volume"]
        * 100
    )


# ============================================================
# 9. SORT
# ============================================================

df_risk_profile = df_risk_profile.sort_values(
    "Date"
).reset_index(drop=True)


# ============================================================
# 10. DISPLAY
# ============================================================

print("\nTransformed shape:")
print(df_risk_profile.shape)

print("\nColumns:")
print(df_risk_profile.columns.tolist())

print("\nFirst 10 rows:")
print(df_risk_profile.head(10))

print("\nMissing values:")
print(df_risk_profile.isna().sum())

print("\nDate range:")
print(df_risk_profile["Date"].min())
print(df_risk_profile["Date"].max())


# ============================================================
# 11. SAVE
# ============================================================

output_path = "data/mortgage_risk_profiles.csv"

df_risk_profile.to_csv(
    output_path,
    index=False
)

print("\nSaved to:")
print(output_path)