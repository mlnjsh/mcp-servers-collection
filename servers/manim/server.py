"""
MCP Server: Manim Animation Renderer
Allows Claude to render mathematical animations using Manim.
"""

import asyncio
import json
import subprocess
import tempfile
import os
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("manim-server")

SCENE_TEMPLATE = '''
from manim import *

class DynamicScene(Scene):
    def construct(self):
{code}
'''


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="render_scene",
            description="Render a Manim animation from Python code. Provide the body of the construct() method.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code for the construct() method body (will be indented automatically)"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Render quality: low (480p15), medium (720p30), high (1080p60)",
                        "default": "low"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="list_scenes",
            description="List available pre-built Manim animation templates",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "render_scene":
        return await render_scene(arguments)
    elif name == "list_scenes":
        return list_scenes()
    raise ValueError(f"Unknown tool: {name}")


async def render_scene(args: dict):
    code = args["code"]
    quality = args.get("quality", "low")
    quality_flag = {"low": "-ql", "medium": "-qm", "high": "-qh"}.get(quality, "-ql")

    # Indent code for the construct method
    indented_code = "\n".join(f"        {line}" for line in code.split("\n"))
    full_code = SCENE_TEMPLATE.format(code=indented_code)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()) as f:
        f.write(full_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["manim", "render", quality_flag, temp_path, "DynamicScene"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return [TextContent(type="text", text=f"Animation rendered successfully.\n\nOutput:\n{result.stdout}")]
        else:
            return [TextContent(type="text", text=f"Render failed:\n{result.stderr}")]
    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Render timed out (120s limit).")]
    finally:
        os.unlink(temp_path)


def list_scenes():
    scenes = [
        {"name": "CircleToSquare", "description": "Morphs a circle into a square"},
        {"name": "SineWave", "description": "Animated sine wave drawing"},
        {"name": "MatrixTransformation", "description": "2D linear transformation visualization"},
        {"name": "GradientDescent", "description": "Gradient descent on a 2D loss surface"},
        {"name": "NeuralNetwork", "description": "Neural network forward pass animation"},
        {"name": "FourierSeries", "description": "Fourier series approximation of square wave"},
        {"name": "EigenvalueVisualization", "description": "Eigenvector stretching under transformation"},
        {"name": "ProbabilityDistributions", "description": "Normal, Poisson, and Binomial distributions"},
    ]
    return [TextContent(type="text", text=json.dumps(scenes, indent=2))]


if __name__ == "__main__":
    import mcp.server.stdio
    asyncio.run(mcp.server.stdio.run(app))
