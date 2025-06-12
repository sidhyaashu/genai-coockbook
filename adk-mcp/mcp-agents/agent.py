# agent.py
import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
MODEL = os.getenv("MODEL", "gemini-2.0-flash")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")
if not EXA_API_KEY:
    raise ValueError("EXA_API_KEY environment variable is not set.")

async def create_agent():
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://127.0.0.1:3333/sse",
            command="npx",
            args=["-y", "exa-mcp-server"],
            env={"EXA_API_KEY": EXA_API_KEY},
        )
    )

    agent = LlmAgent(
        model=MODEL,
        name="fetch_assistant",
        instruction=(
            "You are a helpful assistant that extracts and summarizes data from web pages "
            "using the available MCP tools."
        ),
        tools=tools,
    )
    return agent, exit_stack

async def main():
    agent, exit_stack = await create_agent()
    # Example usage: feed a user query to your agent here
    # run your agent using Runner or adk web which manages exit_stack

if __name__ == "__main__":
    asyncio.run(main())
