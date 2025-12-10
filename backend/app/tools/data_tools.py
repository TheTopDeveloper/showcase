"""
Data Tools Module
=================
Tools for querying structured data (CSV files) with exact lookups.
"""

import pandas as pd
from typing import Optional, Dict

from app.config import STRUCTURED_DATA


class DataTools:
    """Collection of tools for structured data access."""

    def __init__(self):
        self._dataframes: Dict[str, pd.DataFrame] = {}
        self._load_data()

    def _load_data(self):
        """Load all structured data files."""
        for name, path in STRUCTURED_DATA.items():
            if path.exists():
                try:
                    self._dataframes[name] = pd.read_csv(path)
                    print(f"Loaded structured data: {name} ({len(self._dataframes[name])} rows)")
                except Exception as e:
                    print(f"Error loading {name}: {e}")
            else:
                print(f"Warning: Data file not found: {path}")

    def reload_data(self):
        """Reload all data files."""
        self._dataframes.clear()
        self._load_data()


_data_tools: Optional[DataTools] = None


def get_data_tools() -> DataTools:
    """Get or create the data tools singleton."""
    global _data_tools
    if _data_tools is None:
        _data_tools = DataTools()
    return _data_tools


# =============================================================================
# TOOL FUNCTIONS
# =============================================================================

def get_pricing_info(plan_name: Optional[str] = None) -> str:
    """Get pricing information for subscription plans."""
    tools = get_data_tools()
    df = tools._dataframes.get("pricing")

    if df is None:
        return "Pricing information is currently unavailable."

    if plan_name:
        plan_df = df[df["plan_name"].str.lower() == plan_name.lower()]
        if plan_df.empty:
            available = ", ".join(df["plan_name"].tolist())
            return f"Plan '{plan_name}' not found. Available plans: {available}"
        df = plan_df

    results = []
    for _, row in df.iterrows():
        plan_info = f"""
**{row['plan_name']} Plan**
- Monthly: ${row['monthly_price_usd']}/month
- Annual: ${row['annual_price_usd']}/year (${row['annual_monthly_equivalent']}/month equivalent)
- Users: {row['max_users']}
- Storage: {row['storage_gb']}GB
- Projects: {row['projects_limit']}
- Custom Fields: {row['custom_fields']}
- Time Tracking: {row['time_tracking']}
- Priority Support: {row['priority_support']}
- SSO: {row['sso']}
        """.strip()
        results.append(plan_info)

    return "\n\n".join(results)


def compare_plans(plan1: str, plan2: str) -> str:
    """Compare two subscription plans side by side."""
    tools = get_data_tools()
    df = tools._dataframes.get("pricing")

    if df is None:
        return "Pricing information is currently unavailable."

    plan1_df = df[df["plan_name"].str.lower() == plan1.lower()]
    plan2_df = df[df["plan_name"].str.lower() == plan2.lower()]

    if plan1_df.empty:
        return f"Plan '{plan1}' not found."
    if plan2_df.empty:
        return f"Plan '{plan2}' not found."

    p1 = plan1_df.iloc[0]
    p2 = plan2_df.iloc[0]

    comparison = f"""
**{p1['plan_name']} vs {p2['plan_name']} Comparison**

| Feature | {p1['plan_name']} | {p2['plan_name']} |
|---------|---------|---------|
| Monthly Price | ${p1['monthly_price_usd']} | ${p2['monthly_price_usd']} |
| Annual Price | ${p1['annual_price_usd']} | ${p2['annual_price_usd']} |
| Max Users | {p1['max_users']} | {p2['max_users']} |
| Storage | {p1['storage_gb']}GB | {p2['storage_gb']}GB |
| Projects | {p1['projects_limit']} | {p2['projects_limit']} |
| Custom Fields | {p1['custom_fields']} | {p2['custom_fields']} |
| Time Tracking | {p1['time_tracking']} | {p2['time_tracking']} |
| SSO | {p1['sso']} | {p2['sso']} |
    """.strip()

    return comparison


def check_feature_availability(feature_name: str, plan_name: Optional[str] = None) -> str:
    """Check if a specific feature is available and on which plans."""
    tools = get_data_tools()
    df = tools._dataframes.get("features")

    if df is None:
        return "Feature information is currently unavailable."

    matches = df[df["feature_name"].str.lower().str.contains(feature_name.lower())]

    if matches.empty:
        matches = df[df["description"].str.lower().str.contains(feature_name.lower())]

    if matches.empty:
        return f"No feature matching '{feature_name}' found."

    results = []
    for _, row in matches.iterrows():
        feature_info = f"""
**{row['feature_name']}** ({row['feature_category']})
{row['description']}

Availability by plan:
- Free: {row['free']}
- Starter: {row['starter']}
- Professional: {row['professional']}
- Business: {row['business']}
- Enterprise: {row['enterprise']}
        """.strip()

        if plan_name:
            plan_col = plan_name.lower()
            if plan_col in row.index:
                availability = row[plan_col]
                feature_info += f"\n\n→ On {plan_name} plan: {availability}"

        results.append(feature_info)

    return "\n\n---\n\n".join(results)


def get_support_resolution(issue_keyword: str) -> str:
    """Find resolution steps for common support issues."""
    tools = get_data_tools()
    df = tools._dataframes.get("support_issues")

    if df is None:
        return "Support issue database is currently unavailable."

    matches = df[
        df["issue_title"].str.lower().str.contains(issue_keyword.lower()) |
        df["category"].str.lower().str.contains(issue_keyword.lower())
    ]

    if matches.empty:
        return f"No common issues found matching '{issue_keyword}'. Please contact support@nimbusflow.io"

    results = []
    for _, row in matches.iterrows():
        issue_info = f"""
**{row['issue_title']}**
Category: {row['category']}
Typical Resolution Time: {row['avg_resolution_time_hours']} hours

**Resolution Steps:**
{row['resolution']}
        """.strip()
        results.append(issue_info)

    return "\n\n---\n\n".join(results)


def list_all_plans() -> str:
    """List all available subscription plans with basic info."""
    tools = get_data_tools()
    df = tools._dataframes.get("pricing")

    if df is None:
        return "Pricing information is currently unavailable."

    plans = []
    for _, row in df.iterrows():
        price_str = f"${row['monthly_price_usd']}/mo" if row['monthly_price_usd'] != "Custom" else "Custom pricing"
        plans.append(f"- **{row['plan_name']}**: {price_str} - Up to {row['max_users']} users")

    return "**Available Plans:**\n" + "\n".join(plans)


# =============================================================================
# TOOL DEFINITIONS FOR OPENAI
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_pricing_info",
            "description": "Get detailed pricing information for subscription plans.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_name": {
                        "type": "string",
                        "description": "Specific plan name (Free, Starter, Professional, Business, Enterprise).",
                        "enum": ["Free", "Starter", "Professional", "Business", "Enterprise"]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_plans",
            "description": "Compare two subscription plans side by side.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan1": {
                        "type": "string",
                        "description": "First plan to compare",
                        "enum": ["Free", "Starter", "Professional", "Business", "Enterprise"]
                    },
                    "plan2": {
                        "type": "string",
                        "description": "Second plan to compare",
                        "enum": ["Free", "Starter", "Professional", "Business", "Enterprise"]
                    }
                },
                "required": ["plan1", "plan2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_feature_availability",
            "description": "Check if a specific feature is available and on which plans.",
            "parameters": {
                "type": "object",
                "properties": {
                    "feature_name": {
                        "type": "string",
                        "description": "Name or keyword of the feature to check"
                    },
                    "plan_name": {
                        "type": "string",
                        "description": "Optionally check for a specific plan",
                        "enum": ["Free", "Starter", "Professional", "Business", "Enterprise"]
                    }
                },
                "required": ["feature_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_support_resolution",
            "description": "Find resolution steps for common support issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_keyword": {
                        "type": "string",
                        "description": "Keyword describing the issue (e.g., 'login', 'billing', 'slow')"
                    }
                },
                "required": ["issue_keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the company knowledge base for general information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for the knowledge base"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_plans",
            "description": "List all available subscription plans with basic pricing.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "get_pricing_info": get_pricing_info,
    "compare_plans": compare_plans,
    "check_feature_availability": check_feature_availability,
    "get_support_resolution": get_support_resolution,
    "list_all_plans": list_all_plans,
}
