# Data Science MCP Server

Explore, clean, and analyze datasets through Claude without writing code.

## Tools

| Tool | Description |
|------|-------------|
| `describe_data` | Load CSV and get comprehensive summary |
| `correlation_matrix` | Correlation analysis with strong pairs highlighted |
| `clean_data` | Handle missing values, duplicates, outliers |
| `value_counts` | Distribution of categorical columns |
| `detect_outliers` | IQR-based outlier detection |

## Setup

```bash
pip install mcp pandas numpy
claude mcp add data-science python servers/data-science/server.py
```
