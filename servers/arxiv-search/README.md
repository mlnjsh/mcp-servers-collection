# arXiv Search MCP Server

Search, retrieve, and browse academic papers from arXiv directly through Claude.

## Tools

| Tool | Description |
|------|-------------|
| `search_papers` | Search by keyword, author, or category |
| `get_paper` | Get full details of a paper by arXiv ID |
| `recent_papers` | Latest papers in a category (cs.AI, cs.LG, quant-ph, etc.) |

## Setup

```bash
pip install mcp
claude mcp add arxiv python servers/arxiv-search/server.py
```

## Example

Ask Claude: *"Find the latest papers on quantum machine learning from arXiv"*
