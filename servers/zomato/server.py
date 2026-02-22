"""
MCP Server: Zomato Restaurant Search
Search restaurants, menus, and reviews via Zomato's API.

Note: Requires a Zomato API key. Set ZOMATO_API_KEY environment variable.
Alternatively, uses mock data for demonstration.
"""

import asyncio
import json
import os
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("zomato")

API_KEY = os.environ.get("ZOMATO_API_KEY", "")
BASE_URL = "https://developers.zomato.com/api/v2.1"

# Mock data for demonstration when API key is not set
MOCK_RESTAURANTS = [
    {"name": "Biryani House", "cuisine": "Hyderabadi, Biryani", "rating": 4.5, "cost_for_two": 600,
     "location": "Banjara Hills, Hyderabad", "delivery_time": "35 min"},
    {"name": "Paradise Restaurant", "cuisine": "Biryani, North Indian", "rating": 4.3, "cost_for_two": 800,
     "location": "Secunderabad, Hyderabad", "delivery_time": "40 min"},
    {"name": "Meghana Foods", "cuisine": "Andhra, Biryani", "rating": 4.4, "cost_for_two": 500,
     "location": "Koramangala, Bangalore", "delivery_time": "30 min"},
    {"name": "Truffles", "cuisine": "American, Continental", "rating": 4.6, "cost_for_two": 700,
     "location": "Indiranagar, Bangalore", "delivery_time": "25 min"},
    {"name": "Toit Brewpub", "cuisine": "Italian, Continental, Craft Beer", "rating": 4.5, "cost_for_two": 1500,
     "location": "Indiranagar, Bangalore", "delivery_time": "Dine-in only"},
]


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_restaurants",
            description="Search restaurants by name, cuisine, or location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (restaurant name, cuisine, or dish)"},
                    "city": {"type": "string", "description": "City name", "default": "Bangalore"},
                    "sort_by": {"type": "string", "enum": ["rating", "cost", "delivery_time"], "default": "rating"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_restaurant_details",
            description="Get detailed info about a specific restaurant.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Restaurant name"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_cuisines",
            description="List available cuisines in a city.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_restaurants":
        return search_restaurants(arguments)
    elif name == "get_restaurant_details":
        return get_details(arguments)
    elif name == "get_cuisines":
        return get_cuisines(arguments)
    raise ValueError(f"Unknown tool: {name}")


def search_restaurants(args):
    query = args["query"].lower()
    city = args.get("city", "").lower()

    if API_KEY:
        import requests
        headers = {"user-key": API_KEY}
        params = {"q": query, "count": 10}
        resp = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
        if resp.status_code == 200:
            return [TextContent(type="text", text=json.dumps(resp.json(), indent=2))]

    # Mock search
    results = [r for r in MOCK_RESTAURANTS
               if query in r["name"].lower() or query in r["cuisine"].lower()
               or query in r["location"].lower()]

    if not results:
        results = MOCK_RESTAURANTS[:3]

    sort_key = args.get("sort_by", "rating")
    if sort_key == "rating":
        results.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_key == "cost":
        results.sort(key=lambda x: x["cost_for_two"])

    return [TextContent(type="text", text=json.dumps({"results": results, "count": len(results),
                                                       "note": "Using demo data. Set ZOMATO_API_KEY for live results."}, indent=2))]


def get_details(args):
    name = args["name"].lower()
    for r in MOCK_RESTAURANTS:
        if name in r["name"].lower():
            details = {**r, "menu_highlights": ["Dum Biryani", "Butter Chicken", "Gulab Jamun"],
                       "reviews": [{"user": "FoodLover", "rating": 5, "text": "Amazing food!"},
                                   {"user": "CriticalEater", "rating": 4, "text": "Good but crowded."}]}
            return [TextContent(type="text", text=json.dumps(details, indent=2))]
    return [TextContent(type="text", text=f"Restaurant '{args['name']}' not found.")]


def get_cuisines(args):
    cuisines = ["North Indian", "South Indian", "Chinese", "Italian", "Biryani", "Street Food",
                "Continental", "Japanese", "Thai", "Mexican", "Mediterranean", "Korean",
                "American", "Mughlai", "Andhra", "Chettinad", "Bengali", "Rajasthani"]
    return [TextContent(type="text", text=json.dumps({"city": args["city"], "cuisines": sorted(cuisines)}, indent=2))]


if __name__ == "__main__":
    import mcp.server.stdio
    asyncio.run(mcp.server.stdio.run(app))
