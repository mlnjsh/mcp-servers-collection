# Manim MCP Server

Render mathematical animations using [Manim](https://www.manim.community/) directly from Claude.

## Tools

| Tool | Description |
|------|-------------|
| `render_scene` | Render a Manim animation from Python code |
| `list_scenes` | List pre-built animation templates |

## Setup

```bash
pip install manim mcp
claude mcp add manim python servers/manim/server.py
```

## Example

Ask Claude: *"Create a Manim animation that shows a circle morphing into a square, then displays the equation A = s^2"*
