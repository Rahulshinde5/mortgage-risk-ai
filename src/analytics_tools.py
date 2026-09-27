import duckdb
import pandas as pd


DB_FILE = "data/mortgage_risk.duckdb"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return duckdb.connect(DB_FILE, read_only=True)


# ============================================================
# TOOL 1 — LATEST KPIs
# ============================================================

def get_latest_kpis():
    """
    Return the latest available mortgage market KPIs.
    """

    con = get_connection()

    result = con.execute("""
        SELECT
            Date,
            Originations,
            Origination_Volume,
            DPD_30_89,
            DPD_90_PLUS,
            Higher_Risk_Share,
            Average_Mortgage_Size
        FROM executive_kpis
        ORDER BY Date DESC
        LIMIT 1
    """).fetchdf()

    con.close()

    if result.empty:
        return {"error": "No KPI data available."}

    row = result.iloc[0]

    return {
        "date": str(row["Date"].date()),
        "originations": round(float(row["Originations"]), 2),
        "origination_volume": round(float(row["Origination_Volume"]), 2),
        "dpd_30_89": round(float(row["DPD_30_89"]), 2),
        "dpd_90_plus": round(float(row["DPD_90_PLUS"]), 2),
        "higher_risk_share": round(float(row["Higher_Risk_Share"]), 2),
        "average_mortgage_size": round(
            float(row["Average_Mortgage_Size"]), 2
        )
    }


# ============================================================
# TOOL 2 — TREND ANALYSIS
# ============================================================

def analyze_trends(months=12):
    """
    Analyze recent mortgage lending trends.

    Parameters
    ----------
    months : int
        Number of recent months to analyze.
    """

    con = get_connection()

    result = con.execute("""
        SELECT
            Date,
            Originations,
            Origination_Volume,
            Originations_MoM_Pct,
            Originations_YoY_Pct,
            Origination_Volume_MoM_Pct,
            Origination_Volume_YoY_Pct
        FROM executive_kpis
        ORDER BY Date DESC
        LIMIT ?
    """, [months]).fetchdf()

    con.close()

    if result.empty:
        return {"error": "No trend data available."}

    result = result.sort_values("Date")

    latest = result.iloc[-1]

    return {
        "period_start": str(result["Date"].min().date()),
        "period_end": str(result["Date"].max().date()),
        "months_analyzed": len(result),

        "latest_originations": round(
            float(latest["Originations"]), 2
        ),

        "latest_originations_yoy_pct": round(
            float(latest["Originations_YoY_Pct"]), 2
        ),

        "latest_volume_yoy_pct": round(
            float(latest["Origination_Volume_YoY_Pct"]), 2
        ),

        "average_originations": round(
            float(result["Originations"].mean()), 2
        ),

        "average_origination_volume": round(
            float(result["Origination_Volume"].mean()), 2
        )
    }


# ============================================================
# TOOL 3 — CREDIT RISK ANALYSIS
# ============================================================

def analyze_risk(months=12):
    """
    Analyze recent delinquency and borrower credit-risk trends.
    """

    con = get_connection()

    result = con.execute("""
        SELECT
            Date,
            DPD_30_89,
            DPD_90_PLUS,
            Higher_Risk_Share,
            DPD_30_89_YoY_Ppt,
            DPD_90_PLUS_YoY_Ppt,
            Higher_Risk_Share_YoY_Ppt
        FROM executive_kpis
        ORDER BY Date DESC
        LIMIT ?
    """, [months]).fetchdf()

    con.close()

    if result.empty:
        return {"error": "No risk data available."}

    result = result.sort_values("Date")

    latest = result.iloc[-1]

    return {
        "period_start": str(result["Date"].min().date()),
        "period_end": str(result["Date"].max().date()),
        "months_analyzed": len(result),

        "latest_dpd_30_89": round(
            float(latest["DPD_30_89"]), 2
        ),

        "latest_dpd_90_plus": round(
            float(latest["DPD_90_PLUS"]), 2
        ),

        "latest_higher_risk_share": round(
            float(latest["Higher_Risk_Share"]), 2
        ),

        "dpd_30_89_yoy_change_ppt": round(
            float(latest["DPD_30_89_YoY_Ppt"]), 2
        ),

        "dpd_90_plus_yoy_change_ppt": round(
            float(latest["DPD_90_PLUS_YoY_Ppt"]), 2
        ),

        "higher_risk_share_yoy_change_ppt": round(
            float(latest["Higher_Risk_Share_YoY_Ppt"]), 2
        )
    }

# ============================================================
# TOOL 4 — CHANGE DETECTION
# ============================================================

def detect_changes():
    """
    Compare the latest mortgage market metrics with:
    1. Previous month
    2. Same month in the previous year

    Returns verified changes from the DuckDB analytical database.
    """

    con = get_connection()

    result = con.execute("""
        SELECT
            Date,
            Originations,
            Origination_Volume,
            DPD_30_89,
            DPD_90_PLUS,
            Higher_Risk_Share,
            Average_Mortgage_Size
        FROM executive_kpis
        ORDER BY Date DESC
        LIMIT 13
    """).fetchdf()

    con.close()

    if result.empty:
        return {"error": "No KPI data available."}

    result = result.sort_values("Date").reset_index(drop=True)

    latest = result.iloc[-1]
    previous = result.iloc[-2] if len(result) >= 2 else None

    # Find same month previous year
    yoy_row = None

    if len(result) >= 13:
        yoy_row = result.iloc[-13]

    def pct_change(current, previous_value):
        if previous_value == 0:
            return None

        return round(
            ((current - previous_value) / previous_value) * 100,
            2
        )

    def point_change(current, previous_value):
        return round(
            current - previous_value,
            2
        )

    output = {
        "latest_date": str(latest["Date"].date()),

        "previous_month": (
            str(previous["Date"].date())
            if previous is not None
            else None
        ),

        "same_month_previous_year": (
            str(yoy_row["Date"].date())
            if yoy_row is not None
            else None
        ),

        "month_over_month": {
            "originations_pct": pct_change(
                float(latest["Originations"]),
                float(previous["Originations"])
            ) if previous is not None else None,

            "origination_volume_pct": pct_change(
                float(latest["Origination_Volume"]),
                float(previous["Origination_Volume"])
            ) if previous is not None else None,

            "dpd_30_89_ppt": point_change(
                float(latest["DPD_30_89"]),
                float(previous["DPD_30_89"])
            ) if previous is not None else None,

            "dpd_90_plus_ppt": point_change(
                float(latest["DPD_90_PLUS"]),
                float(previous["DPD_90_PLUS"])
            ) if previous is not None else None,

            "higher_risk_share_ppt": point_change(
                float(latest["Higher_Risk_Share"]),
                float(previous["Higher_Risk_Share"])
            ) if previous is not None else None,

            "average_mortgage_size_pct": pct_change(
                float(latest["Average_Mortgage_Size"]),
                float(previous["Average_Mortgage_Size"])
            ) if previous is not None else None,
        },

        "year_over_year": {
            "originations_pct": pct_change(
                float(latest["Originations"]),
                float(yoy_row["Originations"])
            ) if yoy_row is not None else None,

            "origination_volume_pct": pct_change(
                float(latest["Origination_Volume"]),
                float(yoy_row["Origination_Volume"])
            ) if yoy_row is not None else None,

            "dpd_30_89_ppt": point_change(
                float(latest["DPD_30_89"]),
                float(yoy_row["DPD_30_89"])
            ) if yoy_row is not None else None,

            "dpd_90_plus_ppt": point_change(
                float(latest["DPD_90_PLUS"]),
                float(yoy_row["DPD_90_PLUS"])
            ) if yoy_row is not None else None,

            "higher_risk_share_ppt": point_change(
                float(latest["Higher_Risk_Share"]),
                float(yoy_row["Higher_Risk_Share"])
            ) if yoy_row is not None else None,

            "average_mortgage_size_pct": pct_change(
                float(latest["Average_Mortgage_Size"]),
                float(yoy_row["Average_Mortgage_Size"])
            ) if yoy_row is not None else None,
        }
    }

    return output

# ============================================================
# LOCAL TEST
# ============================================================
if __name__ == "__main__":

    print("\n===== TEST 1: LATEST KPIs =====")
    print(get_latest_kpis())

    print("\n===== TEST 2: TREND ANALYSIS =====")
    print(analyze_trends(12))

    print("\n===== TEST 3: RISK ANALYSIS =====")
    print(analyze_risk(12))

    print("\n===== TEST 4: CHANGE DETECTION =====")
    print(detect_changes())