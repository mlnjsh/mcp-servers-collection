"""
MCP Server: arXiv Paper Search
Search, retrieve, and summarize academic papers from arXiv.
"""

import asyncio
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("arxiv-search")

ARXIV_API = "http://export.arxiv.org/api/query"


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_papers",
            description="Search arXiv for papers by keyword, author, or category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (keywords, title, or author)"},
                    "category": {"type": "string", "description": "arXiv category (e.g., cs.AI, cs.LG, cs.CL, quant-ph)"},
                    "max_results": {"type": "integer", "default": 10, "description": "Number of results (max 50)"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_paper",
            description="Get full details of a specific arXiv paper by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "arXiv paper ID (e.g., 2301.07041)"}
                },
                "required": ["paper_id"]
            }
        ),
        Tool(
            name="recent_papers",
            description="Get the most recent papers in a category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "arXiv category (cs.AI, cs.LG, cs.CL, quant-ph, etc.)"},
                    "max_results": {"type": "integer", "default": 10}
                },
                "required": ["category"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_papers":
        return await search_papers(arguments)
    elif name == "get_paper":
        return await get_paper(arguments)
    elif name == "recent_papers":
        return await recent_papers(arguments)
    raise ValueError(f"Unknown tool: {name}")


def parse_arxiv_response(xml_text):
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

    papers = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")[:500]
        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
        paper_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
        published = entry.find("atom:published", ns).text[:10]
        categories = [c.get("term") for c in entry.findall("atom:category", ns)]
        pdf_link = f"https://arxiv.org/pdf/{paper_id}"

        papers.append({
            "id": paper_id,
            "title": title,
            "authors": authors[:5],
            "published": published,
            "abstract": summary,
            "categories": categories[:3],
            "pdf": pdf_link,
            "url": f"https://arxiv.org/abs/{paper_id}"
        })
    return papers


async def search_papers(args):
    query = args["query"]
    max_results = min(args.get("max_results", 10), 50)
    category = args.get("category", "")

    search_query = f"all:{query}"
    if category:
        search_query = f"cat:{category}+AND+all:{query}"

    params = urllib.parse.urlencode({
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    })

    try:
        url = f"{ARXIV_API}?{params}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_text = resp.read().decode()
        papers = parse_arxiv_response(xml_text)
        return [TextContent(type="text", text=json.dumps({"query": query, "count": len(papers), "papers": papers}, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error searching arXiv: {e}")]


async def get_paper(args):
    paper_id = args["paper_id"]
    try:
        url = f"{ARXIV_API}?id_list={paper_id}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_text = resp.read().decode()
        papers = parse_arxiv_response(xml_text)
        if papers:
            return [TextContent(type="text", text=json.dumps(papers[0], indent=2))]
        return [TextContent(type="text", text=f"Paper {paper_id} not found.")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def recent_papers(args):
    category = args["category"]
    max_results = min(args.get("max_results", 10), 50)

    params = urllib.parse.urlencode({
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    })

    try:
        url = f"{ARXIV_API}?{params}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_text = resp.read().decode()
        papers = parse_arxiv_response(xml_text)
        return [TextContent(type="text", text=json.dumps({"category": category, "count": len(papers), "papers": papers}, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


if __name__ == "__main__":
    import mcp.server.stdio
    asyncio.run(mcp.server.stdio.run(app))
