import duckdb
import streamlit as st
import plotly.express as px

from src.claude_agent import ask_claude


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Mortgage Risk Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #101f24;
        --body: #26383d;
        --muted: #3d5055;
        --muted-2: #465a5f;
        --line: #d2dddf;
        --surface: #ffffff;
        --canvas: #f4f7f7;
        --navy: #173b43;
        --navy-2: #214a52;
        --teal: #087f75;
        --teal-soft: #e9f4f2;
        --blue: #3b6f92;
        --orange: #c7832b;
        --red: #c65a52;
        --green: #3d8b67;
    }

    .stApp, [data-testid="stAppViewContainer"] {
        background: var(--canvas);
        color: var(--ink);
        font-family: "Aptos", "Segoe UI", sans-serif;
    }

    [data-testid="stHeader"] { background: transparent; }

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1480px;
        padding-top: 1.45rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        color: var(--ink) !important;
    }

    p, label, [data-testid="stMarkdownContainer"] p {
        color: var(--body);
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
        font-size: 0.94rem;
        line-height: 1.5;
        opacity: 1 !important;
    }

    [data-testid="stMarkdownContainer"] {
        color: var(--body);
    }

    /* ---------------- SIDEBAR ---------------- */
    [data-testid="stSidebar"] {
        background: var(--navy);
        border-right: 1px solid #2b565d;
    }

    [data-testid="stSidebar"] * {
        color: #f3f8f7 !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #dce9e9 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #edf5f4 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #3a5a60 !important;
        margin: 1.15rem 0;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
        color: #e3eeee !important;
        font-size: 0.84rem;
        font-weight: 600;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #214a52 !important;
        border: 1px solid #58777b !important;
        border-radius: 7px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #ffffff !important;
    }

    [data-baseweb="popover"] [role="option"] {
        color: #18323a !important;
        background: #ffffff !important;
    }

    .sidebar-brand {
        padding: 0.2rem 0 0.1rem;
    }

    .sidebar-brand-title {
        font-size: 1.2rem;
        font-weight: 750;
        letter-spacing: -0.02em;
    }

    .sidebar-brand-subtitle {
        margin-top: 0.2rem;
        color: #c7dcdd !important;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
    }

    .sidebar-section {
        margin: 0.2rem 0 0.55rem;
        color: #b9d0d1 !important;
        font-size: 0.70rem;
        font-weight: 750;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }

    .sidebar-nav {
        padding: 0.62rem 0.75rem;
        border-radius: 7px;
        background: #214a52;
        border-left: 3px solid #58aaa2;
        color: #ffffff !important;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    .sidebar-info {
        color: #d6e4e3 !important;
        font-size: 0.82rem;
        line-height: 1.5;
    }

    /* ---------------- HEADER ---------------- */
    .exec-header {
        position: relative;
        padding: 1.65rem 1.8rem;
        margin: 0 0 1.05rem;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(26, 54, 60, 0.035);
        overflow: hidden;
    }

    .exec-header::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 5px;
        background: var(--teal);
    }

    .exec-eyebrow {
        margin: 0 0 0.42rem;
        color: var(--teal) !important;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }

    .exec-header h1 {
        margin: 0;
        color: var(--ink) !important;
        font-size: 2rem;
        line-height: 1.18;
        letter-spacing: -0.025em;
    }

    .exec-header p {
        max-width: 950px;
        margin: 0.62rem 0 0;
        color: #26383d !important;
        font-size: 0.98rem;
        line-height: 1.55;
    }

    /* ---------------- KPI CARDS ---------------- */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.85rem;
        margin: 0.5rem 0 1.35rem;
    }

    .kpi-card {
        position: relative;
        min-height: 118px;
        padding: 1.05rem 1.15rem 0.95rem;
        border: 0;
        border-radius: 9px;
        color: #ffffff !important;
        overflow: hidden;
        box-shadow: 0 3px 10px rgba(26, 54, 60, 0.10);
        transition: transform 0.16s ease, box-shadow 0.16s ease;
    }

    /* Restrained, dashboard-style color cards inspired by the inventory UI. */
    .kpi-card.teal {
        background: linear-gradient(135deg, #087f75 0%, #15958a 100%);
    }
    .kpi-card.blue {
        background: linear-gradient(135deg, #4569a8 0%, #5c79b5 100%);
    }
    .kpi-card.orange {
        background: linear-gradient(135deg, #d9873e 0%, #e5a052 100%);
    }
    .kpi-card.red {
        background: linear-gradient(135deg, #d85d63 0%, #e37178 100%);
    }
    .kpi-card.purple {
        background: linear-gradient(135deg, #7459b5 0%, #856bc0 100%);
    }
    .kpi-card.amber {
        background: linear-gradient(135deg, #d39a35 0%, #e4ad43 100%);
    }

    .kpi-card::after {
        content: "";
        position: absolute;
        width: 90px;
        height: 90px;
        right: -28px;
        top: -34px;
        border-radius: 50%;
        background: rgba(255,255,255,0.07);
        pointer-events: none;
    }

    .kpi-label {
        color: rgba(255,255,255,0.92) !important;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        position: relative;
        z-index: 1;
    }

    .kpi-value {
        margin-top: 0.42rem;
        color: #ffffff !important;
        font-size: 1.72rem;
        font-weight: 750;
        line-height: 1.1;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }

    .kpi-meta {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.18rem 0.48rem;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 5px;
        color: #ffffff !important;
        font-size: 0.72rem;
        font-weight: 650;
        position: relative;
        z-index: 1;
    }

    /* ---------------- INTERACTION ---------------- */
    .kpi-card {
        transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 9px 22px rgba(26, 54, 60, 0.16);
    }

    .pulse-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.7rem;
        margin: 0.15rem 0 1.1rem;
    }

    .pulse-item {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        min-height: 44px;
        padding: 0.55rem 0.75rem;
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 7px;
        color: #26383d !important;
        font-size: 0.78rem;
        font-weight: 650;
    }

    .pulse-marker {
        width: 8px;
        height: 8px;
        flex: 0 0 8px;
        border-radius: 50%;
    }

    .pulse-up { background: #2f8c70; }
    .pulse-watch { background: #c7832b; }
    .pulse-stable { background: #4c7894; }

    .section-heading {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 0.15rem 0 0.2rem;
    }

    .section-heading .bar {
        width: 4px;
        height: 24px;
        border-radius: 3px;
        background: var(--teal);
    }

    .section-heading .title {
        color: var(--ink) !important;
        font-size: 1.25rem;
        font-weight: 750;
    }

    .section-subtitle {
        margin: 0 0 0.85rem;
        color: var(--muted) !important;
        font-size: 0.9rem;
    }

    .chart-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 9px;
        padding: 0.2rem 0.2rem 0;
        box-shadow: 0 2px 8px rgba(26, 54, 60, 0.025);
    }

    .quick-label {
        color: #34494e !important;
    }

    [data-testid="stAppViewContainer"] div.stButton > button {
        transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
    }

    [data-testid="stAppViewContainer"] div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 9px rgba(26, 54, 60, 0.08);
    }

    [data-testid="stTextAreaRootElement"] textarea {
        font-weight: 500;
    }

    .response-box {
        margin-top: 0.8rem;
        padding: 1rem 1.1rem;
        background: #fbfcfc;
        border: 1px solid #cbd8da;
        border-left: 4px solid var(--teal);
        border-radius: 8px;
    }

    .response-box * {
        color: #263d42 !important;
    }

    /* ---------------- AI ANALYST ---------------- */
    .ai-shell {
        background: #ffffff;
        border: 1px solid #cfdedd;
        border-top: 4px solid var(--teal);
        border-radius: 10px;
        padding: 1.25rem 1.3rem 1.3rem;
        margin: 0.15rem 0 1.4rem;
        box-shadow: 0 3px 12px rgba(26, 54, 60, 0.045);
    }

    .ai-title-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }

    .ai-icon {
        width: 34px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        background: var(--teal-soft);
        color: var(--teal) !important;
        font-weight: 800;
        font-size: 0.78rem;
        border: 1px solid #c9e2de;
    }

    .ai-title {
        margin: 0;
        color: var(--ink) !important;
        font-size: 1.35rem;
        font-weight: 750;
    }

    .ai-description {
        margin: 0.45rem 0 1rem;
        color: #26383d !important;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .quick-label {
        margin-bottom: 0.45rem;
        color: var(--muted-2) !important;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    [data-testid="stAppViewContainer"] div.stButton > button {
        min-height: 42px;
        background: #ffffff;
        color: var(--ink) !important;
        border: 1px solid #b9c9ca;
        border-radius: 7px;
        font-size: 0.86rem;
        font-weight: 650;
        transition: 0.15s ease;
    }

    [data-testid="stAppViewContainer"] div.stButton > button:hover {
        background: #e9f4f2;
        color: #075f59 !important;
        border-color: #63a69f;
        transform: translateY(-2px);
        box-shadow: 0 5px 12px rgba(26, 54, 60, 0.10);
    }

    [data-testid="stAppViewContainer"] div.stButton > button:focus-visible {
        outline: 2px solid #087f75 !important;
        outline-offset: 2px;
    }

    [data-testid="stAppViewContainer"] div.stButton > button[kind="primary"] {
        background: var(--teal);
        border-color: var(--teal);
        color: #ffffff !important;
        min-width: 105px;
    }

    [data-testid="stAppViewContainer"] div.stButton > button[kind="primary"]:hover {
        background: #066a62;
        border-color: #066a62;
        color: #ffffff !important;
    }

    /* Streamlit renders button text inside nested elements. Explicitly style
       every nested text node so the primary Analyze button never inherits
       the dark page text color. */
    [data-testid="stAppViewContainer"] [data-testid="baseButton-primary"],
    [data-testid="stAppViewContainer"] button[kind="primary"] {
        background: #087f75 !important;
        border: 1px solid #087f75 !important;
        color: #ffffff !important;
        min-height: 46px !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 750 !important;
        box-shadow: 0 3px 8px rgba(8, 127, 117, 0.18) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease !important;
    }

    [data-testid="stAppViewContainer"] [data-testid="baseButton-primary"] *,
    [data-testid="stAppViewContainer"] button[kind="primary"] * {
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"] [data-testid="baseButton-primary"]:hover,
    [data-testid="stAppViewContainer"] button[kind="primary"]:hover {
        background: #066a62 !important;
        border-color: #066a62 !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 7px 15px rgba(8, 127, 117, 0.25) !important;
    }

    [data-testid="stTextAreaRootElement"] {
        background: #ffffff !important;
        border: 1px solid #aebfc1 !important;
        border-radius: 7px !important;
    }

    [data-testid="stTextAreaRootElement"]:focus-within {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 2px rgba(8, 127, 117, 0.10) !important;
    }

    [data-testid="stTextAreaRootElement"] textarea {
        background: #ffffff !important;
        color: var(--ink) !important;
        caret-color: var(--ink);
        font-size: 0.94rem;
        line-height: 1.5;
    }

    [data-testid="stTextAreaRootElement"] textarea::placeholder {
        color: #465b60 !important;
        opacity: 1;
    }

    [data-testid="stTextArea"] label {
        color: var(--ink) !important;
        font-size: 0.86rem;
        font-weight: 700;
    }

    .response-header {
        margin: 1rem 0 0.55rem;
        padding-top: 0.85rem;
        border-top: 1px solid var(--line);
        color: var(--ink) !important;
        font-size: 1.05rem;
        font-weight: 750;
    }

    /* ---------------- TABS ---------------- */
    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.2rem;
        border-bottom: 1px solid var(--line);
    }

    [data-testid="stTab"] {
        color: #26383d !important;
        font-size: 0.9rem;
        font-weight: 700;
        padding: 0.68rem 1rem;
    }

    [data-testid="stTab"] p {
        color: inherit !important;
        font-size: 0.9rem !important;
        font-weight: inherit !important;
    }

    [data-testid="stTab"][aria-selected="true"] {
        color: var(--teal) !important;
        border-bottom-color: var(--teal) !important;
    }

    /* ---------------- TABLE ---------------- */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] [role="gridcell"],
    [data-testid="stDataFrame"] [role="columnheader"] {
        color: #182d32 !important;
    }

    /* ---------------- STATUS ---------------- */
    .status-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin: 0.55rem 0 0.75rem;
    }

    .status-card {
        transition: transform 0.14s ease, box-shadow 0.14s ease, border-color 0.14s ease;
        display: flex;
        align-items: center;
        gap: 0.55rem;
        min-height: 52px;
        padding: 0.72rem 0.9rem;
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 8px;
        color: #26383d !important;
        font-size: 0.82rem;
        font-weight: 650;
    }

    .status-card:hover {
        transform: translateY(-1px);
        border-color: #b8cacc;
        box-shadow: 0 4px 12px rgba(26, 54, 60, 0.07);
    }

    .status-dot {
        width: 9px;
        height: 9px;
        flex: 0 0 9px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 0 3px #e5f2ec;
    }

    .footer-note {
        margin-top: 0.6rem;
        color: var(--muted-2) !important;
        font-size: 0.76rem;
    }

    @media (max-width: 900px) {
        .kpi-grid, .status-grid { grid-template-columns: 1fr 1fr; }
        .pulse-strip { grid-template-columns: 1fr; }
    }

    @media (max-width: 650px) {
        [data-testid="stAppViewContainer"] .main .block-container {
            padding: 1rem 0.8rem 2rem;
        }
        .kpi-grid, .status-grid { grid-template-columns: 1fr; }
        .exec-header { padding: 1.25rem 1.15rem; }
        .exec-header h1 { font-size: 1.55rem; }
    }

    /* ---------------- FINAL READABILITY PASS ---------------- */
    /* Strong typography on light/white surfaces. */
    .exec-header h1,
    .section-heading .title,
    .ai-title,
    .response-header,
    h1, h2, h3, h4 {
        color: #101f24 !important;
        font-weight: 750 !important;
    }

    .exec-header p,
    .ai-description,
    .section-subtitle,
    .pulse-item,
    .status-card,
    .footer-note,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stMarkdownContainer"] p {
        color: #26383d !important;
        opacity: 1 !important;
    }

    .quick-label,
    .exec-eyebrow {
        font-weight: 800 !important;
    }

    [data-testid="stTextArea"] label,
    [data-testid="stSelectbox"] label {
        color: #172a2f !important;
        font-weight: 750 !important;
    }

    /* Keep the intentionally white text on colored KPI cards. */
    .kpi-card,
    .kpi-card * {
        color: #ffffff !important;
    }

    /* Strong, readable tab labels. */
    [data-testid="stTab"],
    [data-testid="stTab"] p {
        color: #26383d !important;
        font-weight: 750 !important;
    }

    [data-testid="stTab"][aria-selected="true"],
    [data-testid="stTab"][aria-selected="true"] p {
        color: #087f75 !important;
        font-weight: 800 !important;
    }

    /* Strong table typography. */
    [data-testid="stDataFrame"] [role="gridcell"],
    [data-testid="stDataFrame"] [role="columnheader"] {
        color: #182d32 !important;
    }

    /* Make the normal text area and placeholder clearly readable. */
    [data-testid="stTextAreaRootElement"] textarea {
        color: #101f24 !important;
    }

    [data-testid="stTextAreaRootElement"] textarea::placeholder {
        color: #465b60 !important;
        opacity: 1 !important;
    }

    /* Make quick-prompt labels dark on their white buttons. */
    [data-testid="stAppViewContainer"] div.stButton > button,
    [data-testid="stAppViewContainer"] div.stButton > button p {
        color: #172a2f !important;
        font-weight: 700 !important;
    }

    [data-testid="stAppViewContainer"] div.stButton > button:hover,
    [data-testid="stAppViewContainer"] div.stButton > button:hover p {
        color: #075f59 !important;
    }

    /* Analyze button remains white text on teal. */
    [data-testid="stAppViewContainer"] [data-testid="baseButton-primary"],
    [data-testid="stAppViewContainer"] [data-testid="baseButton-primary"] *,
    [data-testid="stAppViewContainer"] button[kind="primary"],
    [data-testid="stAppViewContainer"] button[kind="primary"] * {
        color: #ffffff !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "data/mortgage_risk.duckdb"


@st.cache_data
def load_dashboard_data():

    con = duckdb.connect(DB_FILE, read_only=True)

    df = con.execute("""
        SELECT
            k.*,
            r.Deep_Subprime_Share,
            r.Subprime_Share,
            r.Near_Prime_Share,
            r.Prime_Share,
            r.Super_Prime_Share
        FROM executive_kpis k
        LEFT JOIN mortgage_risk_profiles r
            ON CAST(k.Date AS DATE) = CAST(r.Date AS DATE)
        ORDER BY k.Date
    """).fetchdf()

    con.close()

    return df


df = load_dashboard_data()

latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest


# ============================================================
# SIDEBAR AND PRESENTATION CONTROLS
# ============================================================

period_options = {
    "Last 3 months": 3,
    "Last 6 months": 6,
    "Last 12 months": 12,
    "Last 24 months": 24,
    "Full history": None,
}

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">Mortgage Risk</div>
            <div class="sidebar-brand-subtitle">LENDING &amp; CREDIT INTELLIGENCE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown('<div class="sidebar-section">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-nav">Overview<br>Lending Trends<br>Credit Risk<br>AI Analyst</div>',
        unsafe_allow_html=True,
    )
    selected_period = st.selectbox(
        "Chart and table period",
        list(period_options),
        index=2,
    )
    visible_months = period_options[selected_period]
    view_df = df if visible_months is None else df.tail(visible_months)
    st.divider()
    st.markdown('<div class="sidebar-section">Data Source</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-info">Consumer Financial Protection Bureau (CFPB)<br>Public mortgage data</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section" style="margin-top:1.1rem;">Technology</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-info">Python · DuckDB · Plotly<br>Streamlit · Claude</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        f'<div class="sidebar-info"><b>Data through</b><br>{latest["Date"].strftime("%B %Y")}<br><br><b>Showing</b><br>{len(view_df):,} monthly observations</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# EXECUTIVE HEADER AND SECTION NAVIGATION
# ============================================================

st.markdown(
    f"""
    <section class="exec-header">
        <div class="exec-eyebrow">Mortgage market intelligence</div>
        <h1>Mortgage Lending &amp; Credit Risk Intelligence</h1>
        <p>Executive analytics powered by public CFPB data, with an AI analyst for lending,
        delinquency and borrower credit-risk questions.</p>
    </section>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Analytical period: January 2008 – {latest['Date'].strftime('%B %Y')}")

def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font={"family": "Aptos, Segoe UI, sans-serif", "color": "#36545a", "size": 12},
        title={"font": {"size": 15, "color": "#18323a"}, "x": 0},
        margin={"l": 12, "r": 18, "t": 50, "b": 12},
        height=345,
        hovermode="x unified",
        hoverlabel={"bgcolor": "#ffffff", "bordercolor": "#dce5e5", "font": {"color": "#17282b"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"orientation": "h", "y": -0.2, "x": 0, "title": {"text": ""}},
    )
    fig.update_xaxes(
        title_text="",
        showgrid=False,
        showline=True,
        linecolor="#dce5e5",
        tickfont={"color": "#46585b", "size": 13},
        hoverformat="%b %Y",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e3eaeb",
        zeroline=False,
        tickfont={"color": "#46585b", "size": 13},
    )
    return fig

def set_analyst_prompt(prompt_text):
    st.session_state["analyst_prompt"] = prompt_text


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown(
    f"""
    <div class="section-heading">
        <span class="bar"></span><span class="title">Executive Overview</span>
    </div>
    <div class="section-subtitle">Latest reported month · {latest['Date'].strftime('%B %Y')}</div>
    """,
    unsafe_allow_html=True,
)

originations_mom = ((latest["Originations"] - previous["Originations"]) / previous["Originations"] * 100) if previous["Originations"] else 0
volume_mom = ((latest["Origination_Volume"] - previous["Origination_Volume"]) / previous["Origination_Volume"] * 100) if previous["Origination_Volume"] else 0
dpd30_mom = latest["DPD_30_89"] - previous["DPD_30_89"]
dpd90_mom = latest["DPD_90_PLUS"] - previous["DPD_90_PLUS"]
risk_mom = latest["Higher_Risk_Share"] - previous["Higher_Risk_Share"]
size_mom = ((latest["Average_Mortgage_Size"] - previous["Average_Mortgage_Size"]) / previous["Average_Mortgage_Size"] * 100) if previous["Average_Mortgage_Size"] else 0

st.markdown(
    f"""
    <div class="pulse-strip">
        <div class="pulse-item"><span class="pulse-marker pulse-up"></span>
            Lending activity&nbsp; <strong>+{originations_mom:.2f}% MoM</strong>
        </div>
        <div class="pulse-item"><span class="pulse-marker pulse-watch"></span>
            30–89 DPD&nbsp; <strong>{dpd30_mom:+.2f} ppt MoM</strong>
        </div>
        <div class="pulse-item"><span class="pulse-marker pulse-stable"></span>
            90+ DPD&nbsp; <strong>{dpd90_mom:+.2f} ppt MoM</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

def signed(value, suffix="%"):
    return f"{value:+.2f}{suffix}"

st.markdown(
    f"""
    <div class="kpi-grid">
        <div class="kpi-card teal">
            <div class="kpi-label">Mortgage Originations</div>
            <div class="kpi-value">{latest['Originations']:,.0f}</div>
            <div class="kpi-meta">MoM {signed(originations_mom)}</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-label">Origination Volume</div>
            <div class="kpi-value">${latest['Origination_Volume'] / 1e9:.2f}B</div>
            <div class="kpi-meta">MoM {signed(volume_mom)}</div>
        </div>
        <div class="kpi-card orange">
            <div class="kpi-label">30–89 DPD</div>
            <div class="kpi-value">{latest['DPD_30_89']:.1f}%</div>
            <div class="kpi-meta">MoM {signed(dpd30_mom, ' ppt')}</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-label">90+ DPD</div>
            <div class="kpi-value">{latest['DPD_90_PLUS']:.1f}%</div>
            <div class="kpi-meta">MoM {signed(dpd90_mom, ' ppt')}</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-label">Higher-Risk Share</div>
            <div class="kpi-value">{latest['Higher_Risk_Share']:.2f}%</div>
            <div class="kpi-meta">MoM {signed(risk_mom, ' ppt')}</div>
        </div>
        <div class="kpi-card amber">
            <div class="kpi-label">Average Mortgage Size</div>
            <div class="kpi-value">${latest['Average_Mortgage_Size']:,.0f}</div>
            <div class="kpi-meta">MoM {signed(size_mom)}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ai-shell">
        <div class="ai-title-row">
            <div class="ai-icon">AI</div>
            <div class="ai-title">AI Mortgage Analyst</div>
        </div>
        <div class="ai-description">
            Ask business questions about lending, delinquency, borrower risk or recent mortgage-market changes.
            Claude selects the relevant analytical tools and uses verified DuckDB results.
        </div>
        <div class="quick-label">Quick prompts</div>
    </div>
    """,
    unsafe_allow_html=True,
)

prompt_columns = st.columns(3)
quick_prompts = [
    "What changed in the mortgage market recently?",
    "Analyze lending trends",
    "Analyze credit risk",
]
for prompt_column, quick_prompt in zip(prompt_columns, quick_prompts):
    prompt_column.button(
        quick_prompt,
        key=f"quick_prompt_{quick_prompt}",
        use_container_width=True,
        on_click=set_analyst_prompt,
        args=(quick_prompt,),
    )

prompt = st.text_area(
    "Your question",
    key="analyst_prompt",
    placeholder="Example: Originations have increased over the last year. Is the borrower risk profile also becoming riskier?",
    height=105,
)

analyze_col, _ = st.columns([1.35, 4.65])
with analyze_col:
    analyze_clicked = st.button("✨  Analyze", type="primary", key="analyze_prompt", use_container_width=True)

if analyze_clicked:
    if not prompt.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("AI analyst is analyzing the mortgage data..."):
            try:
                answer = ask_claude(prompt.strip())
                st.markdown('<div class="response-header">Analyst Response</div>', unsafe_allow_html=True)
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown(answer)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Unable to complete the analysis: {e}")


overview_tab, lending_tab, risk_tab = st.tabs(
    ["Executive Overview", "Lending", "Credit Risk"]
)


# ============================================================
# LENDING TRENDS
# ============================================================

with lending_tab:
    st.markdown(
        f"""
        <div class="section-heading">
            <span class="bar" style="background:#3b6f92;"></span>
            <span class="title">Lending Trends</span>
        </div>
        <div class="section-subtitle">Monthly lending activity · {selected_period.lower()}</div>
        """,
        unsafe_allow_html=True,
    )
    chart_columns = st.columns(2)

    with chart_columns[0]:
        fig_originations = px.line(
            view_df,
            x="Date",
            y="Originations",
            markers=True,
            title="Mortgage Originations",
            color_discrete_sequence=["#087f75"],
        )
        style_chart(fig_originations)
        fig_originations.update_layout(yaxis_title="Loans")
        fig_originations.update_yaxes(tickformat=",.0f")
        fig_originations.update_traces(
            line={"width": 3},
            marker={"size": 6},
            hovertemplate="%{x|%b %Y}<br>Originations: %{y:,.0f}<extra></extra>",
        )
        st.plotly_chart(fig_originations, use_container_width=True)

    with chart_columns[1]:
        volume_df = view_df.copy()
        volume_df["Origination_Volume_B"] = volume_df["Origination_Volume"] / 1e9
        fig_volume = px.line(
            volume_df,
            x="Date",
            y="Origination_Volume_B",
            markers=True,
            title="Origination Volume",
            color_discrete_sequence=["#3375a5"],
        )
        style_chart(fig_volume)
        fig_volume.update_layout(yaxis_title="Volume ($B)")
        fig_volume.update_yaxes(tickprefix="$", ticksuffix="B", tickformat=".2f")
        fig_volume.update_traces(
            line={"width": 3},
            marker={"size": 6},
            hovertemplate="%{x|%b %Y}<br>Volume: $%{y:.2f}B<extra></extra>",
        )
        st.plotly_chart(fig_volume, use_container_width=True)


# ============================================================
# CREDIT RISK
# ============================================================

with risk_tab:
    st.markdown(
        f"""
        <div class="section-heading">
            <span class="bar" style="background:#c7832b;"></span>
            <span class="title">Credit Risk &amp; Delinquency</span>
        </div>
        <div class="section-subtitle">Delinquency and borrower mix · {selected_period.lower()}</div>
        """,
        unsafe_allow_html=True,
    )

    delinq_df = view_df[["Date", "DPD_30_89", "DPD_90_PLUS"]].copy()
    delinq_long = delinq_df.melt(
        id_vars="Date",
        value_vars=["DPD_30_89", "DPD_90_PLUS"],
        var_name="Metric",
        value_name="Percentage",
    )
    delinq_long["Metric"] = delinq_long["Metric"].replace(
        {"DPD_30_89": "30–89 DPD", "DPD_90_PLUS": "90+ DPD"}
    )

    risk_df = view_df[
        [
            "Date",
            "Deep_Subprime_Share",
            "Subprime_Share",
            "Near_Prime_Share",
            "Prime_Share",
            "Super_Prime_Share",
        ]
    ].copy()
    risk_long = risk_df.melt(
        id_vars="Date",
        var_name="Credit Segment",
        value_name="Share",
    )
    risk_long["Credit Segment"] = (
        risk_long["Credit Segment"]
        .str.replace("_Share", "", regex=False)
        .str.replace("_", " ", regex=False)
    )

    fig_columns = st.columns(2)
    with fig_columns[0]:
        fig_dpd = px.line(
            delinq_long,
            x="Date",
            y="Percentage",
            color="Metric",
            markers=True,
            title="Delinquency Trends",
            color_discrete_map={"30–89 DPD": "#d18a27", "90+ DPD": "#bd5146"},
        )
        style_chart(fig_dpd)
        fig_dpd.update_layout(yaxis_title="Share (%)")
        fig_dpd.update_yaxes(ticksuffix="%", tickformat=".1f")
        fig_dpd.update_traces(
            line={"width": 2.5},
            marker={"size": 5},
            hovertemplate="%{x|%b %Y}<br>%{fullData.name}: %{y:.1f}%<extra></extra>",
        )
        st.plotly_chart(fig_dpd, use_container_width=True)

    with fig_columns[1]:
        fig_risk = px.area(
            risk_long,
            x="Date",
            y="Share",
            color="Credit Segment",
            title="Borrower Credit Risk Composition",
            color_discrete_sequence=["#b9574d", "#d18a27", "#4a9b91", "#3375a5", "#183e49"],
        )
        style_chart(fig_risk)
        fig_risk.update_layout(yaxis_title="Share (%)")
        fig_risk.update_yaxes(ticksuffix="%", tickformat=".1f")
        fig_risk.update_traces(
            hovertemplate="%{x|%b %Y}<br>%{fullData.name}: %{y:.2f}%<extra></extra>"
        )
        st.plotly_chart(fig_risk, use_container_width=True)


# ============================================================
# RECENT METRICS
# ============================================================

with overview_tab:
    st.divider()
    st.subheader("Recent Mortgage Risk Metrics")
    st.caption(f"Latest {min(12, len(view_df))} monthly observations in the selected period")

    recent_df = view_df[
        [
            "Date",
            "Originations",
            "Origination_Volume",
            "DPD_30_89",
            "DPD_90_PLUS",
            "Higher_Risk_Share",
            "Average_Mortgage_Size",
        ]
    ].tail(12).copy()
    recent_df["Origination_Volume"] = recent_df["Origination_Volume"] / 1e9
    recent_df = recent_df.rename(
        columns={
            "Date": "Month",
            "Origination_Volume": "Volume ($B)",
            "DPD_30_89": "30–89 DPD (%)",
            "DPD_90_PLUS": "90+ DPD (%)",
            "Higher_Risk_Share": "Higher-Risk Share (%)",
            "Average_Mortgage_Size": "Avg Mortgage Size ($)",
        }
    )
    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Month": st.column_config.DateColumn("Month", format="MMM YYYY"),
            "Originations": st.column_config.NumberColumn(format="%,.0f"),
            "Volume ($B)": st.column_config.NumberColumn(format="$%.2fB"),
            "30–89 DPD (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "90+ DPD (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Higher-Risk Share (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Avg Mortgage Size ($)": st.column_config.NumberColumn(format="$%,.0f"),
        },
    )


with overview_tab:
    st.divider()
    st.subheader("Data & Automation Status")
    st.markdown(
        """
        <div class="status-grid">
            <div class="status-card"><span class="status-dot"></span>Data pipeline validated</div>
            <div class="status-card"><span class="status-dot"></span>DuckDB analytical layer active</div>
            <div class="status-card"><span class="status-dot"></span>AI analytical tools active</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Higher-Risk Share is a derived analytical metric (Deep Subprime + Subprime)."
    )

st.markdown(
    '<div class="footer-note">Data source: Consumer Financial Protection Bureau (CFPB) · AI analysis powered by Claude</div>',
    unsafe_allow_html=True,
)