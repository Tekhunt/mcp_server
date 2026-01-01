#!/usr/bin/env python3
"""
MCP Server with Pydantic Models - SSE HTTP Transport
Provides type-safe tool inputs and structured outputs over HTTP with SSE
"""
import sys
from pathlib import Path

# Add project root to path if running directly
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

import logging
from typing import Any, Optional
from datetime import datetime
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
import uvicorn
#!/usr/bin/env python3
import sys
# from pathlib import Path

# # Add the project root (3 levels up from this file) to Python path
# project_root = Path(__file__).resolve().parent.parent.parent.parent
# sys.path.insert(0, str(project_root))

# Now your imports will work
from src.servers.models.local_models import (
    CalculateInput,
    CalculateOutput,
    WeatherInput,
    WeatherOutput,
    NoteInput,
    NoteOutput,
    TemperatureInput,
    TemperatureOutput,
    FileReadInput,
    FileReadOutput,
    TimeInput,
    TimeOutput,
    ErrorOutput,
)
import os

# Rest of your imports and code...
from dotenv import load_dotenv
# from ..models.local_models import *

# from servers.models.local_models import CalculateInput

# Load environment variables
load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("pydantic-mcp-server")

# ============================================================================
# TOOL IMPLEMENTATIONS - Using Pydantic models
# ============================================================================

def calculate(arguments: dict[str, Any]) -> list[TextContent]:
    """Perform calculations with validated inputs and structured output"""
    try:
        # Validate input
        input_data = CalculateInput(**arguments)
        
        # Perform calculation
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y
        }
        
        result = operations[input_data.operation](input_data.a, input_data.b)
        
        # Create structured output
        output = CalculateOutput(
            operation=input_data.operation,
            operand_a=input_data.a,
            operand_b=input_data.b,
            result=result,
            formatted=f"{input_data.a} {input_data.operation} {input_data.b} = {result}"
        )
        
        logger.info(f"Calculation: {output.formatted}")
        
        # Return as JSON
        return [TextContent(
            type="text",
            text=output.model_dump_json(indent=2)
        )]
        
    except Exception as e:
        error = ErrorOutput(
            error_type=type(e).__name__,
            error_message=str(e)
        )
        logger.error(f"Error in calculate: {e}")
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]


def get_weather(arguments: dict[str, Any]) -> list[TextContent]:
    """Get weather with validated inputs and structured output"""
    try:
        # Validate input
        input_data = WeatherInput(**arguments)
        
        # Simulated weather data
        output = WeatherOutput(
            city=input_data.city,
            temperature="72°F",
            temperature_celsius=22.2,
            condition="Sunny",
            humidity="45%",
            wind="10 mph"
        )
        
        logger.info(f"Weather requested for: {input_data.city}")
        
        return [TextContent(
            type="text",
            text=output.model_dump_json(indent=2)
        )]
        
    except Exception as e:
        error = ErrorOutput(
            error_type=type(e).__name__,
            error_message=str(e)
        )
        logger.error(f"Error in get_weather: {e}")
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]


def save_note(arguments: dict[str, Any]) -> list[TextContent]:
    """Save note with validated inputs and structured output"""
    try:
        # Validate input
        input_data = NoteInput(**arguments)
        
        # Create safe filename
        filename = f"note_{input_data.title.replace(' ', '_')}.txt"
        
        # Write note with metadata
        with open(filename, 'w') as f:
            f.write(f"Title: {input_data.title}\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            if input_data.tags:
                f.write(f"Tags: {', '.join(input_data.tags)}\n")
            f.write(f"\n{input_data.content}")
        
        # Create structured output
        output = NoteOutput(
            filename=filename,
            title=input_data.title,
            content_length=len(input_data.content),
            tags=input_data.tags,
            message=f"Note successfully saved to {filename}"
        )
        
        logger.info(f"Note saved: {filename}")
        
        return [TextContent(
            type="text",
            text=output.model_dump_json(indent=2)
        )]
        
    except Exception as e:
        error = ErrorOutput(
            error_type=type(e).__name__,
            error_message=str(e)
        )
        logger.error(f"Error in save_note: {e}")
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]


def convert_temperature(arguments: dict[str, Any]) -> list[TextContent]:
    """Convert temperature with validated inputs and structured output"""
    try:
        # Validate input
        input_data = TemperatureInput(**arguments)
        
        # Convert
        celsius = (input_data.temperature_fahrenheit - 32) * 5.0 / 9.0
        
        # Create structured output
        output = TemperatureOutput(
            fahrenheit=input_data.temperature_fahrenheit,
            celsius=round(celsius, 2),
            formatted=f"{input_data.temperature_fahrenheit}°F = {celsius:.2f}°C"
        )
        
        logger.info(f"Temperature conversion: {output.formatted}")
        
        return [TextContent(
            type="text",
            text=output.model_dump_json(indent=2)
        )]
        
    except Exception as e:
        error = ErrorOutput(
            error_type=type(e).__name__,
            error_message=str(e)
        )
        logger.error(f"Error in convert_temperature: {e}")
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]


def read_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Read file with validated inputs and structured output"""
    try:
        # Validate input
        input_data = FileReadInput(**arguments)
        
        # Read file
        with open(input_data.filename, 'r') as f:
            content = f.read()
        
        # Create structured output
        output = FileReadOutput(
            filename=input_data.filename,
            content=content,
            size_bytes=len(content.encode('utf-8')),
            lines=len(content.splitlines())
        )
        
        logger.info(f"File read: {input_data.filename}")
        
        return [TextContent(
            type="text",
            text=output.model_dump_json(indent=2)
        )]
        
    except FileNotFoundError:
        error = ErrorOutput(
            error_type="FileNotFoundError",
            error_message=f"File '{arguments.get('filename')}' not found"
        )
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]
    except Exception as e:
        error = ErrorOutput(
            error_type=type(e).__name__,
            error_message=str(e)
        )
        logger.error(f"Error in read_file: {e}")
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]


def get_time(arguments: dict[str, Any]) -> list[TextContent]:
    """Get time with validated inputs and structured output"""
    try:
        # Validate input
        input_data = TimeInput(**arguments)
        
        now = datetime.now()
        
        # Format based on request
        if input_data.format == "iso":
            formatted = now.isoformat()
        elif input_data.format == "human":
            formatted = now.strftime("%B %d, %Y at %I:%M:%S %p")
        else:  # unix
            formatted = str(int(now.timestamp()))
        
        # Create structured output
        output = TimeOutput(
            timestamp=now,
            formatted=formatted,
            format_type=input_data.format
        )
        
        logger.info(f"Time requested in format: {input_data.format}")
        
        return [TextContent(
            type="text",
            text=output.model_dump_json(indent=2)
        )]
        
    except Exception as e:
        error = ErrorOutput(
            error_type=type(e).__name__,
            error_message=str(e)
        )
        logger.error(f"Error in get_time: {e}")
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]


# Tool handler registry
TOOL_HANDLERS = {
    "calculate": calculate,
    "get_weather": get_weather,
    "save_note": save_note,
    "convert_temperature": convert_temperature,
    "read_file": read_file,
    "get_time": get_time,
}


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools with Pydantic schema"""
    return [
        Tool(
            name="calculate",
            description="Perform arithmetic calculations with type-safe inputs and structured output",
            inputSchema=CalculateInput.model_json_schema()
        ),
        Tool(
            name="get_weather",
            description="Get weather information with validated city input and structured JSON output",
            inputSchema=WeatherInput.model_json_schema()
        ),
        Tool(
            name="save_note",
            description="Save a note with optional tags, validated inputs, and structured output",
            inputSchema=NoteInput.model_json_schema()
        ),
        Tool(
            name="convert_temperature",
            description="Convert Fahrenheit to Celsius with validation and structured output",
            inputSchema=TemperatureInput.model_json_schema()
        ),
        Tool(
            name="read_file",
            description="Read file contents with path traversal protection and structured output",
            inputSchema=FileReadInput.model_json_schema()
        ),
        Tool(
            name="get_time",
            description="Get current time in various formats with structured output",
            inputSchema=TimeInput.model_json_schema()
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution with Pydantic validation"""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    if name in TOOL_HANDLERS:
        return TOOL_HANDLERS[name](arguments)
    else:
        error = ErrorOutput(
            error_type="UnknownToolError",
            error_message=f"Unknown tool: {name}"
        )
        logger.warning(f"Unknown tool requested: {name}")
        return [TextContent(type="text", text=error.model_dump_json(indent=2))]


# ============================================================================
# SSE HTTP TRANSPORT SETUP
# ============================================================================

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that serves the MCP server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        """Handle SSE connections"""
        try:
            logger.info(f"New SSE connection from {request.client.host}")
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
            logger.info("SSE connection closed")
            return Response(status_code=204)
        except Exception as e:
            logger.error(f"Error in SSE handler: {e}", exc_info=True)
            return Response(
                content=f"Internal Server Error: {str(e)}\n",
                status_code=500,
                media_type="text/plain"
            )

    async def health_check(request: Request):
        """Health check endpoint"""
        return JSONResponse({
            "status": "healthy",
            "server": "Pydantic MCP Server (SSE)",
            "endpoints": {
                "sse": "/sse",
                "messages": "/messages/",
                "health": "/health"
            },
            "tools": list(TOOL_HANDLERS.keys())
        })
    
    async def list_tools_endpoint(request: Request):
        """List available tools via HTTP"""
        tools_list = await list_tools()
        return JSONResponse({
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools_list
            ]
        })

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/health", endpoint=health_check),
            Route("/tools", endpoint=list_tools_endpoint),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


# def main():
#     """Run the MCP server with SSE HTTP transport"""
#     logger.info("Starting Pydantic MCP server with SSE HTTP transport...")
    
#     # Create Starlette app with SSE support
#     starlette_app = create_starlette_app(app, debug=True)
    
#     port = 8080
#     logger.info(f"SSE endpoint: {MCP_SERVER_URL}:{port}/sse")
#     logger.info(f"Health check: {MCP_SERVER_URL}:{port}/health")
#     logger.info(f"Tools list: {MCP_SERVER_URL}:{port}/tools")
#     logger.info(f"Available tools: {list(TOOL_HANDLERS.keys())}")
    
#     # Run the server using uvicorn
#     uvicorn.run(
#         starlette_app,
#         host="0.0.0.0",
#         port=port,
#         log_level="info"
#     )

import os

def main():
    """Run the MCP server with SSE HTTP transport"""
    logger.info("Starting Pydantic MCP server with SSE HTTP transport...")
    
    # Create Starlette app with SSE support
    starlette_app = create_starlette_app(app, debug=False)  # Set debug=False for production
    
    # Use PORT from environment (Render provides this)
    port = int(os.environ.get("PORT", 8080))
    
    logger.info(f"SSE endpoint: http://0.0.0.0:{port}/sse")
    logger.info(f"Health check: http://0.0.0.0:{port}/health")
    logger.info(f"Tools list: http://0.0.0.0:{port}/tools")
    logger.info(f"Available tools: {list(TOOL_HANDLERS.keys())}")
    
    # Run the server using uvicorn
    uvicorn.run(
        starlette_app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()

  