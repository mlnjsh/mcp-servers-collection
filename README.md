# MCP Servers Collection

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

> A collection of **Model Context Protocol (MCP)** servers that extend Claude and other AI assistants with powerful tools — from rendering mathematical animations to ordering food.

[MCP](https://modelcontextprotocol.io/) is Anthropic's open standard for connecting AI models to external tools, data sources, and services. Each server in this collection provides a set of tools that Claude can use to perform real-world tasks.

---

## Available Servers

| Server | Description | Tools |
|--------|-------------|-------|
| [**Manim**](servers/manim/) | Render mathematical animations with Manim | `render_scene`, `list_scenes`, `preview_animation` |
| [**ML Toolkit**](servers/ml-toolkit/) | Train, evaluate, and explain ML models | `train_model`, `evaluate`, `feature_importance`, `predict` |
| [**Data Science**](servers/data-science/) | Data exploration, cleaning, and visualization | `describe_data`, `plot`, `clean_data`, `correlation_matrix` |
| [**Zomato**](servers/zomato/) | Search restaurants, menus, and reviews via Zomato API | `search_restaurants`, `get_menu`, `get_reviews`, `get_cuisines` |
| [**Swiggy**](servers/swiggy/) | Browse restaurants and food delivery via Swiggy | `search_food`, `get_restaurant`, `get_offers`, `track_order` |
| [**arXiv Search**](servers/arxiv-search/) | Search and summarize academic papers from arXiv | `search_papers`, `get_paper`, `get_citations`, `summarize` |

---

## Quick Start

### Prerequisites

```bash
pip install mcp numpy pandas scikit-learn matplotlib manim requests
```

### Running a Server

```bash
# Run the ML Toolkit server
python servers/ml-toolkit/server.py

# Run the Manim server
python servers/manim/server.py

# Run the Data Science server
python servers/data-science/server.py
```

### Connecting to Claude Code

```bash
# Add any server to Claude Code
claude mcp add manim-server python servers/manim/server.py
claude mcp add ml-toolkit python servers/ml-toolkit/server.py
claude mcp add data-science python servers/data-science/server.py
claude mcp add zomato python servers/zomato/server.py
claude mcp add arxiv python servers/arxiv-search/server.py
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ml-toolkit": {
      "command": "python",
      "args": ["path/to/servers/ml-toolkit/server.py"]
    },
    "manim": {
      "command": "python",
      "args": ["path/to/servers/manim/server.py"]
    }
  }
}
```

---

## Server Details

### Manim Server

Render beautiful mathematical animations directly from Claude.

**Tools:**
- `render_scene` — Render a Manim scene from Python code
- `list_scenes` — List available pre-built animation scenes
- `preview_animation` — Quick preview at low quality

**Example prompt:** *"Create a Manim animation showing gradient descent on a 3D surface"*

### ML Toolkit Server

Train and evaluate ML models interactively through Claude.

**Tools:**
- `train_model` — Train a model (linear regression, random forest, XGBoost, etc.)
- `evaluate` — Get metrics (accuracy, F1, RMSE, confusion matrix)
- `feature_importance` — Explain which features matter most
- `predict` — Make predictions on new data
- `cross_validate` — Run k-fold cross-validation

**Example prompt:** *"Load iris.csv, train a random forest classifier, and show feature importance"*

### Data Science Server

Explore, clean, and visualize datasets without writing code.

**Tools:**
- `describe_data` — Summary statistics, dtypes, missing values
- `plot` — Create matplotlib/seaborn visualizations
- `clean_data` — Handle missing values, outliers, encoding
- `correlation_matrix` — Compute and visualize correlations
- `profile` — Generate a comprehensive data profile report

**Example prompt:** *"Load sales_data.csv, show me the distribution of revenue, and identify outliers"*

### Zomato Server

Search restaurants, browse menus, and read reviews.

**Tools:**
- `search_restaurants` — Search by name, cuisine, location
- `get_menu` — Get restaurant menu with prices
- `get_reviews` — Read user reviews and ratings
- `get_cuisines` — List available cuisines in a city

**Example prompt:** *"Find the top-rated biryani restaurants in Hyderabad with reviews"*

### Swiggy Server

Browse food delivery options and restaurants.

**Tools:**
- `search_food` — Search for dishes or restaurants
- `get_restaurant` — Get restaurant details and menu
- `get_offers` — Current deals and discounts
- `nearby_restaurants` — Find restaurants near a location

**Example prompt:** *"What are the best pizza deals on Swiggy near Koramangala, Bangalore?"*

### arXiv Search Server

Search, retrieve, and summarize academic papers.

**Tools:**
- `search_papers` — Search arXiv by keyword, author, or category
- `get_paper` — Get full paper details (abstract, authors, PDF link)
- `recent_papers` — Latest papers in a category (cs.AI, cs.LG, etc.)
- `summarize` — Generate a summary of a paper's abstract

**Example prompt:** *"Find the latest papers on diffusion models from the last week"*

---

## Architecture

Each MCP server follows the same structure:

```
servers/server-name/
  server.py       # Main MCP server implementation
  tools.py        # Tool implementations
  README.md       # Server-specific documentation
  requirements.txt
```

All servers use the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

```python
# Basic server structure
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("server-name")

@app.list_tools()
async def list_tools():
    return [Tool(name="tool_name", description="...", inputSchema={...})]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "tool_name":
        result = do_something(arguments)
        return [TextContent(type="text", text=str(result))]
```

---

## Building Your Own MCP Server

1. Pick an API or tool you want to expose
2. Copy `servers/arxiv-search/` as a template
3. Define your tools in `tools.py`
4. Register them in `server.py`
5. Test with `claude mcp add your-server python servers/your-server/server.py`

See the [MCP documentation](https://modelcontextprotocol.io/) for the full spec.

---

## Contributing

PRs welcome! To add a new server:
1. Create a new folder under `servers/`
2. Follow the existing structure
3. Add documentation in the server's `README.md`
4. Update this main README with your server

## License

MIT
