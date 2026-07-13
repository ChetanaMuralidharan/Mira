import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVERS = {
    "database": "http://127.0.0.1:8765/mcp",
    "vector": "http://127.0.0.1:8766/mcp",
}


async def call_mcp_tool(server: str, tool_name: str, arguments: dict) -> dict:
    url = SERVERS[server]
    try:
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                text = result.content[0].text if result.content else "{}"
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"raw": text}
    except Exception as e:
        return {"error": f"MCP call to '{server}' server failed (tool={tool_name}): {e}"}