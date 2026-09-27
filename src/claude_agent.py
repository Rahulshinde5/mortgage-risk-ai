import json
import os

from dotenv import load_dotenv
from anthropic import Anthropic

from src.analytics_tools import (
    get_latest_kpis,
    analyze_trends,
    analyze_risk,
    detect_changes,
)

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY was not found. Check your .env file."
    )

client = Anthropic(api_key=api_key)


# ============================================================
# CLAUDE ANALYTICAL TOOLS
# ============================================================

TOOLS = [

    # --------------------------------------------------------
    # TOOL 1 — LATEST KPIs
    # --------------------------------------------------------

    {
        "name": "get_latest_kpis",
        "description": (
            "Get the latest mortgage lending and credit risk KPIs "
            "from the DuckDB analytical database. Use this when the "
            "user asks about the latest, current, or most recent metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },

    # --------------------------------------------------------
    # TOOL 2 — TREND ANALYSIS
    # --------------------------------------------------------

    {
        "name": "analyze_trends",
        "description": (
            "Analyze mortgage lending trends over a specified number "
            "of recent months. Returns originations, origination volume, "
            "year-over-year changes, and averages."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "description": "Number of recent months to analyze.",
                    "minimum": 1,
                    "maximum": 60,
                }
            },
            "required": ["months"],
        },
    },

    # --------------------------------------------------------
    # TOOL 3 — CREDIT RISK ANALYSIS
    # --------------------------------------------------------

    {
        "name": "analyze_risk",
        "description": (
            "Analyze mortgage delinquency and borrower credit-risk "
            "trends over a specified number of recent months. Returns "
            "30-89 DPD, 90+ DPD, and higher-risk borrower share metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "description": "Number of recent months to analyze.",
                    "minimum": 1,
                    "maximum": 60,
                }
            },
            "required": ["months"],
        },
    },

    # --------------------------------------------------------
    # TOOL 4 — CHANGE DETECTION
    # --------------------------------------------------------

    {
        "name": "detect_changes",
        "description": (
            "Detect recent changes in mortgage lending and credit-risk "
            "metrics. Compares the latest available month with the "
            "previous month and the same month in the previous year. "
            "Use this when the user asks what changed, recent movements, "
            "month-over-month changes, year-over-year changes, or "
            "movements in mortgage market risk metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(tool_name, tool_input):
    """
    Execute an analytical tool selected by Claude.
    """

    if tool_name == "get_latest_kpis":
        return get_latest_kpis()

    if tool_name == "analyze_trends":
        months = tool_input.get("months", 12)
        return analyze_trends(months)

    if tool_name == "analyze_risk":
        months = tool_input.get("months", 12)
        return analyze_risk(months)

    if tool_name == "detect_changes":
        return detect_changes()

    raise ValueError(f"Unknown tool: {tool_name}")


# ============================================================
# CLAUDE SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Business Analyst specializing in mortgage lending
and credit-risk analytics.

You have access to analytical tools connected to a DuckDB database
containing CFPB mortgage data.

Your responsibilities:

1. Understand the user's business question.
2. Decide which analytical tool or tools are required.
3. Use the tools instead of guessing or calculating metrics yourself.
4. Never invent numbers, dates, percentages, or trends.
5. Numerical statements must be based on tool results.
6. Clearly distinguish observed facts from interpretations or hypotheses.
7. Do not claim causation unless the available data directly supports it.
8. If the data does not contain enough information to explain why
   something happened, explicitly say that the cause cannot be
   determined from the available data.
9. Do not introduce external economic factors such as unemployment,
   inflation, interest rates, home prices, or policy changes unless
   they are provided by an analytical tool.
10. Keep answers clear and useful for a business stakeholder.
11. Highlight important changes, trends, and relationships that are
    directly observable in the returned data.
12. When useful, provide a concise "What this means" section, but
    keep it grounded in the available evidence.
13. When discussing changes, clearly state whether the comparison is
    month-over-month or year-over-year.
14. Do not describe a metric as "significant" unless the data provides
    an explicit threshold or the user asks for a descriptive assessment.

Tool selection:

- Latest/current KPIs → use get_latest_kpis
- Lending/origination trends → use analyze_trends
- Delinquency/credit-risk trends → use analyze_risk
- What changed/recent movements/MoM/YoY comparisons → use detect_changes
- Questions involving multiple areas → use all relevant tools.

Important terminology:

- 30–89 DPD and 90+ DPD are delinquency measures from the CFPB
  mortgage performance data.
- Higher-Risk Share is a derived analytical metric calculated as
  Deep Subprime Share + Subprime Share.
- Do not present Higher-Risk Share as an official CFPB-defined metric.
- The database contains aggregated public data, not individual
  borrower-level records.

The analytical database is the source of truth.
"""


# ============================================================
# CLAUDE AGENT
# ============================================================

def ask_claude(user_prompt):
    """
    Send a user question to Claude and allow Claude to
    select and execute analytical tools.
    """

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    # --------------------------------------------------------
    # First Claude call:
    # Claude determines which analytical tool(s) are required.
    # --------------------------------------------------------

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    # --------------------------------------------------------
    # Continue tool execution until Claude produces
    # a final natural-language response.
    # --------------------------------------------------------

    while response.stop_reason == "tool_use":

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        tool_results = []

        for block in response.content:

            if block.type == "tool_use":

                result = execute_tool(
                    block.name,
                    block.input,
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(
                            result,
                            default=str,
                        ),
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

    # --------------------------------------------------------
    # Extract Claude's final text response
    # --------------------------------------------------------

    final_text = ""

    for block in response.content:

        if block.type == "text":
            final_text += block.text

    return final_text