#!/usr/bin/env python3
"""
Autonomous OpenAI Client with MCP Integration (SSE HTTP Transport)
This version can chain multiple tool calls autonomously without user confirmation
Connects to MCP server via HTTP/SSE instead of stdio
"""

import asyncio
import json
import os
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI()

# MCP Server URL (SSE endpoint)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")


async def run_autonomous_agent():
    """Run the agent with autonomous multi-step tool execution"""
    
    print(f"🚀 Starting Autonomous MCP Agent (SSE HTTP)...")
    print(f"🌐 Connecting to: {MCP_SERVER_URL}\n")
    
    try:
        async with sse_client(url=MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get available tools
                tools_response = await session.list_tools()
                available_tools = tools_response.tools
                
                print("🔧 Available MCP Tools:")
                for tool in available_tools:
                    print(f"  - {tool.name}: {tool.description}")
                print()
                
                # Convert MCP tools to OpenAI function format
                openai_tools = []
                for tool in available_tools:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    })
                
                # Chat loop
                messages = [
                    {
                        "role": "system",
                        "content": """You are a helpful autonomous assistant with access to tools via MCP. 
                        
Key behaviors:
1. When given a multi-step task, execute ALL steps autonomously without asking for confirmation
2. Chain tool calls together to complete complex workflows
3. Only ask for clarification if the task is truly ambiguous
4. After completing all steps, provide a summary of what was accomplished
5. Be proactive and efficient in completing tasks"""
                    }
                ]
                
                print("💬 Chat with the autonomous assistant (type 'quit' to exit)")
                print("💡 Tip: Try multi-step tasks - the agent will complete them autonomously!\n")
                
                while True:
                    # Get user input
                    try:
                        user_input = input("You: ").strip()
                    except (EOFError, KeyboardInterrupt):
                        print("\nGoodbye! 👋")
                        break
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("Goodbye! 👋")
                        break
                    
                    if not user_input:
                        continue
                    
                    # Add user message
                    messages.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    try:
                        # Keep executing until no more tool calls are needed
                        max_iterations = 10  # Prevent infinite loops
                        iteration = 0
                        
                        while iteration < max_iterations:
                            iteration += 1
                            
                            # Call OpenAI API
                            response = await client.chat.completions.create(
                                model="gpt-4",
                                messages=messages,
                                tools=openai_tools,
                                tool_choice="auto"
                            )
                            
                            assistant_message = response.choices[0].message
                            
                            # Add assistant message to conversation
                            messages.append({
                                "role": "assistant",
                                "content": assistant_message.content,
                                "tool_calls": assistant_message.tool_calls
                            })
                            
                            # If no tool calls, we're done with this turn
                            if not assistant_message.tool_calls:
                                if assistant_message.content:
                                    print(f"\nAssistant: {assistant_message.content}\n")
                                break
                            
                            # Execute all tool calls in this batch
                            print(f"\n🔨 Executing tools (Step {iteration})...\n")
                            
                            for tool_call in assistant_message.tool_calls:
                                tool_name = tool_call.function.name
                                tool_args = json.loads(tool_call.function.arguments)
                                
                                print(f"  🔧 {tool_name}")
                                print(f"     Args: {json.dumps(tool_args, indent=6)}")
                                
                                # Call the MCP tool via HTTP/SSE
                                result = await session.call_tool(tool_name, tool_args)
                                
                                # Extract text content from result
                                tool_result = ""
                                for content in result.content:
                                    if hasattr(content, 'text'):
                                        tool_result += content.text
                                
                                print(f"     ✓ Result:\n{tool_result}\n")
                                
                                # Add tool result to messages
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": tool_result
                                })
                        
                        if iteration >= max_iterations:
                            print("⚠️  Maximum iterations reached. Stopping to prevent infinite loop.\n")
                    
                    except Exception as e:
                        print(f"❌ Error: {e}\n")
                        # Remove the last user message to keep conversation state clean
                        if messages[-1]["role"] == "user":
                            messages.pop()
    
    except ConnectionError as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Ensure MCP server is running: python pydantic_mcp_sse_server.py")
        print(f"2. Check server URL: {MCP_SERVER_URL}")
        print(f"3. Verify server health: curl {MCP_SERVER_URL.replace('/sse', '/health')}")
        print(f"4. Check firewall settings if connecting remotely")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def check_server_health():
    """Check if the MCP server is running and healthy"""
    import aiohttp
    
    health_url = MCP_SERVER_URL.replace('/sse', '/health')
    
    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(health_url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Server is healthy")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Server: {data.get('server')}")
                    if 'tools' in data:
                        print(f"   Tools: {', '.join(data['tools'])}")
                    print()
                    return True
                else:
                    print(f"⚠️  Server returned status {response.status}")
                    return False
    except Exception as e:
        print(f"⚠️  Cannot connect to server: {e}")
        print(f"   Make sure the server is running on {MCP_SERVER_URL}")
        return False


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Check server health before starting
    print("🔍 Checking MCP server health...\n")
    server_healthy = asyncio.run(check_server_health())
    
    if not server_healthy:
        print("\n❌ Server health check failed. Please start the MCP server first:")
        print("   python pydantic_mcp_sse_server.py\n")
        exit(1)
    
    # Run the agent
    asyncio.run(run_autonomous_agent())

    