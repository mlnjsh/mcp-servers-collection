"""
MCP Server: Swiggy Food Delivery
Browse restaurants, search food, and check offers via Swiggy.

Note: Uses mock data for demonstration. Swiggy does not have a public API.
For production use, implement web scraping or use Swiggy Partner APIs.
"""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("swiggy")

MOCK_DATA = {
    "restaurants": [
        {"name": "Meghana Foods", "cuisine": "Biryani, Andhra", "rating": 4.4, "delivery_time": "30-35 min",
         "cost_for_two": 500, "offers": ["60% off up to 120", "Free delivery"], "area": "Koramangala"},
        {"name": "Burger King", "cuisine": "American, Burgers", "rating": 4.1, "delivery_time": "20-25 min",
         "cost_for_two": 400, "offers": ["Buy 1 Get 1", "20% off"], "area": "HSR Layout"},
        {"name": "Dominos Pizza", "cuisine": "Pizza, Italian", "rating": 4.0, "delivery_time": "25-30 min",
         "cost_for_two": 600, "offers": ["50% off up to 100"], "area": "Multiple Locations"},
        {"name": "A2B Pure Veg", "cuisine": "South Indian, Vegetarian", "rating": 4.3, "delivery_time": "35-40 min",
         "cost_for_two": 350, "offers": ["Free delivery above 199"], "area": "Jayanagar"},
        {"name": "Behrouz Biryani", "cuisine": "Mughlai, Biryani", "rating": 4.2, "delivery_time": "40-45 min",
         "cost_for_two": 700, "offers": ["Flat 100 off"], "area": "Cloud Kitchen"},
    ],
    "trending": ["Butter Chicken", "Biryani", "Pizza", "Pav Bhaji", "Shawarma", "Dosa", "Momos"]
}


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_food",
            description="Search for dishes or restaurants on Swiggy.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Dish or restaurant name"},
                    "area": {"type": "string", "description": "Area/locality"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_offers",
            description="Get current Swiggy offers and deals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {"type": "string", "description": "Area to check offers for"}
                }
            }
        ),
        Tool(
            name="trending_now",
            description="Get trending dishes and restaurants.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="nearby_restaurants",
            description="Find restaurants near a location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {"type": "string", "description": "Area/locality name"},
                    "cuisine": {"type": "string", "description": "Filter by cuisine type"}
                },
                "required": ["area"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_food":
        query = arguments["query"].lower()
        results = [r for r in MOCK_DATA["restaurants"]
                   if query in r["name"].lower() or query in r["cuisine"].lower()]
        if not results:
            results = MOCK_DATA["restaurants"][:3]
        return [TextContent(type="text", text=json.dumps({"results": results, "query": arguments["query"],
                                                           "note": "Demo data. Swiggy API integration pending."}, indent=2))]
    elif name == "get_offers":
        offers = [{"restaurant": r["name"], "offers": r["offers"]} for r in MOCK_DATA["restaurants"] if r["offers"]]
        return [TextContent(type="text", text=json.dumps({"offers": offers}, indent=2))]
    elif name == "trending_now":
        return [TextContent(type="text", text=json.dumps({"trending_dishes": MOCK_DATA["trending"],
                                                           "top_restaurants": [r["name"] for r in sorted(
                                                               MOCK_DATA["restaurants"], key=lambda x: x["rating"], reverse=True)[:3]]}, indent=2))]
    elif name == "nearby_restaurants":
        area = arguments["area"].lower()
        results = MOCK_DATA["restaurants"]
        if arguments.get("cuisine"):
            results = [r for r in results if arguments["cuisine"].lower() in r["cuisine"].lower()]
        return [TextContent(type="text", text=json.dumps({"area": arguments["area"], "restaurants": results}, indent=2))]
    raise ValueError(f"Unknown tool: {name}")


if __name__ == "__main__":
    import mcp.server.stdio
    asyncio.run(mcp.server.stdio.run(app))
