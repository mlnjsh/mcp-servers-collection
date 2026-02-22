# Zomato MCP Server

Search restaurants, browse menus, and read reviews through Claude.

## Tools

| Tool | Description |
|------|-------------|
| `search_restaurants` | Search by name, cuisine, or location |
| `get_restaurant_details` | Detailed info with menu and reviews |
| `get_cuisines` | Available cuisines in a city |

## Setup

```bash
pip install mcp requests
export ZOMATO_API_KEY="your-api-key"  # Optional, uses demo data without it
claude mcp add zomato python servers/zomato/server.py
```
