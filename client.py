# to start:  python client.py

import asyncio
import nest_asyncio

from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import (
    FunctionAgent, 
    ToolCallResult, 
    ToolCall)
from llama_index.core.workflow import Context
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

nest_asyncio.apply()

llm = Ollama(model="llama3.2", request_timeout=120.0)
Settings.llm = llm

mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
mcp_tools = McpToolSpec(client=mcp_client) # you can also pass list of allowed tools

SYSTEM_PROMPT = """\
    You are an AI assistant for tool calling, and you specialize in NFL sports statistics.

    You are able to use tools to provide SQL queries to a database of sports statistics.
    """


async def list_tools():
    tools = await mcp_tools.to_tool_list_async()
    for tool in tools:
        print(tool.metadata.name, tool.metadata.description)


async def get_agent(tools: McpToolSpec):
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
            name="Agent",
            description="An agent that can provide SQL queries to a database.",
            tools=tools,
            llm=Ollama(model="llama3.2"),
            system_prompt=SYSTEM_PROMPT,
        )
    return agent


async def handle_user_message(
        message_content: str,
        agent: FunctionAgent,
        agent_context: Context,
        verbose: bool = False,
    ):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and type(event) == ToolCall:
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and type(event) == ToolCallResult:
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    return str(response)


async def main():

    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    mcp_tool = McpToolSpec(client=mcp_client)

    print("Available MCP tools:\n")

    await list_tools()

    # get the agent
    agent = await get_agent(mcp_tool)

    # create the agent context
    agent_context = Context(agent)

    try:
        user_input = "which NFL wide receiver had the most receiving yards in week 1 of the 2025 season?"

        print(f"\nUser input: {user_input}")

        print("\n\nGenerating non-MCP response ...")
        response = llm.chat([ChatMessage(role="user",content=user_input)])
        print(f"\nnon-MCP response: {response.message.content}")

        print("\n\nGenerating MCP response ...")
        response = await handle_user_message(user_input, agent, agent_context, verbose=False)
        print(f"\nMCP response: {response}\n\n")

    except KeyboardInterrupt:
        print("Exiting...")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print(f"Closing client...")


if __name__ == "__main__":
    asyncio.run(main())