"""
MCP Server: Data Science Toolkit
Data exploration, cleaning, and visualization through Claude.
"""

import asyncio
import json
import io
import base64
import numpy as np
import pandas as pd
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("data-science")

_data = {"df": None, "path": None}


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="describe_data",
            description="Load and describe a CSV dataset — shape, dtypes, missing values, statistics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to CSV file"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="correlation_matrix",
            description="Compute correlation matrix for numeric columns.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="clean_data",
            description="Clean data: handle missing values, remove duplicates, encode categoricals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "strategy": {
                        "type": "string",
                        "enum": ["drop_na", "fill_median", "fill_mean", "fill_mode"],
                        "default": "fill_median"
                    },
                    "drop_duplicates": {"type": "boolean", "default": True},
                    "output_path": {"type": "string", "description": "Path to save cleaned data"}
                },
                "required": ["strategy"]
            }
        ),
        Tool(
            name="value_counts",
            description="Get value counts for a categorical column.",
            inputSchema={
                "type": "object",
                "properties": {
                    "column": {"type": "string", "description": "Column name"}
                },
                "required": ["column"]
            }
        ),
        Tool(
            name="detect_outliers",
            description="Detect outliers using IQR method.",
            inputSchema={
                "type": "object",
                "properties": {
                    "column": {"type": "string", "description": "Column to check for outliers"}
                },
                "required": ["column"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "describe_data":
        return describe_data(arguments)
    elif name == "correlation_matrix":
        return correlation_matrix()
    elif name == "clean_data":
        return clean_data(arguments)
    elif name == "value_counts":
        return value_counts(arguments)
    elif name == "detect_outliers":
        return detect_outliers(arguments)
    raise ValueError(f"Unknown tool: {name}")


def describe_data(args):
    try:
        df = pd.read_csv(args["path"])
        _data["df"] = df
        _data["path"] = args["path"]

        info = {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "missing_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            "numeric_summary": df.describe().round(3).to_dict(),
            "duplicates": int(df.duplicated().sum()),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 2)
        }
        return [TextContent(type="text", text=json.dumps(info, indent=2, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


def correlation_matrix():
    if _data["df"] is None:
        return [TextContent(type="text", text="No data loaded. Use describe_data first.")]

    numeric = _data["df"].select_dtypes(include=[np.number])
    corr = numeric.corr().round(3)

    # Find strong correlations
    strong = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            val = corr.iloc[i, j]
            if abs(val) > 0.5:
                strong.append({
                    "pair": f"{corr.columns[i]} <-> {corr.columns[j]}",
                    "correlation": val
                })

    result = {
        "matrix": corr.to_dict(),
        "strong_correlations": sorted(strong, key=lambda x: abs(x["correlation"]), reverse=True)
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


def clean_data(args):
    if _data["df"] is None:
        return [TextContent(type="text", text="No data loaded.")]

    df = _data["df"].copy()
    actions = []

    if args.get("drop_duplicates", True):
        before = len(df)
        df = df.drop_duplicates()
        actions.append(f"Removed {before - len(df)} duplicate rows")

    strategy = args.get("strategy", "fill_median")
    missing_before = df.isnull().sum().sum()

    if strategy == "drop_na":
        df = df.dropna()
    elif strategy == "fill_median":
        df[df.select_dtypes(include=[np.number]).columns] = df.select_dtypes(include=[np.number]).fillna(
            df.select_dtypes(include=[np.number]).median()
        )
    elif strategy == "fill_mean":
        df[df.select_dtypes(include=[np.number]).columns] = df.select_dtypes(include=[np.number]).fillna(
            df.select_dtypes(include=[np.number]).mean()
        )

    actions.append(f"Handled {missing_before} missing values using {strategy}")

    if args.get("output_path"):
        df.to_csv(args["output_path"], index=False)
        actions.append(f"Saved to {args['output_path']}")

    _data["df"] = df
    return [TextContent(type="text", text=f"Data cleaned.\n\nActions:\n" + "\n".join(f"- {a}" for a in actions))]


def value_counts(args):
    if _data["df"] is None:
        return [TextContent(type="text", text="No data loaded.")]
    col = args["column"]
    if col not in _data["df"].columns:
        return [TextContent(type="text", text=f"Column '{col}' not found.")]
    vc = _data["df"][col].value_counts().head(20).to_dict()
    return [TextContent(type="text", text=json.dumps(vc, indent=2, default=str))]


def detect_outliers(args):
    if _data["df"] is None:
        return [TextContent(type="text", text="No data loaded.")]
    col = args["column"]
    data = _data["df"][col].dropna()
    Q1, Q3 = data.quantile(0.25), data.quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    outliers = data[(data < lower) | (data > upper)]
    result = {
        "column": col,
        "Q1": round(float(Q1), 3),
        "Q3": round(float(Q3), 3),
        "IQR": round(float(IQR), 3),
        "lower_bound": round(float(lower), 3),
        "upper_bound": round(float(upper), 3),
        "outlier_count": len(outliers),
        "outlier_pct": round(len(outliers) / len(data) * 100, 2)
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


if __name__ == "__main__":
    import mcp.server.stdio
    asyncio.run(mcp.server.stdio.run(app))
