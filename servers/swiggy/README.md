# Swiggy MCP Server

Browse food delivery options from Swiggy through Claude.

## Tools

| Tool | Description |
|------|-------------|
| `search_food` | Search dishes or restaurants |
| `get_offers` | Current deals and discounts |
| `trending_now` | Trending dishes and top restaurants |
| `nearby_restaurants` | Find restaurants near a location |

## Setup

```bash
pip install mcp
claude mcp add swiggy python servers/swiggy/server.py
```

## Note

Uses demo data. Swiggy does not have a public API — for production, implement web scraping or use partner APIs.
