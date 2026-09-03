"""how much of the agent's context window does each server design spend before the user asks anything?

three servers over the same prefect api:
  1. one-to-one: FastMCP.from_openapi over the prefect rest spec
  2. designed:   the hand-written prefect-mcp-server (a dozen tools, read-only), run via uvx --from prefect-mcp
  3. code mode:  the one-to-one server behind a CodeMode transform

run: uv run demos/context_tax.py
"""

import asyncio
import json
from pathlib import Path

import httpx2

from fastmcp import Client, FastMCP
from fastmcp.client.transports import StdioTransport
from fastmcp.experimental.transforms.code_mode import CodeMode

PREFECT_API = "http://localhost:4200/api"


async def measure(label: str, client: Client) -> None:
    async with client:
        tools = await client.list_tools()
    listing = json.dumps([t.model_dump(mode="json", exclude_none=True) for t in tools])
    print(f"{label:<14} {len(tools):>4} tools  {len(listing):>8,} bytes  ~{len(listing) // 4:>6,} tokens")


async def main() -> None:
    spec = httpx2.get(f"{PREFECT_API}/openapi.json").json()
    one_to_one = FastMCP.from_openapi(
        openapi_spec=spec,
        client=httpx2.AsyncClient(base_url=PREFECT_API),
        name="prefect (one-to-one)",
    )
    await measure("one-to-one", Client(one_to_one))

    designed = StdioTransport(
        "uvx",
        ["--from", "prefect-mcp", "prefect-mcp-server"],
        env={"PREFECT_API_URL": PREFECT_API},
        log_file=Path("/dev/null"),
    )
    await measure("designed", Client(designed, mode="legacy"))

    code_mode = FastMCP.from_openapi(
        openapi_spec=spec,
        client=httpx2.AsyncClient(base_url=PREFECT_API),
        name="prefect (code mode)",
        transforms=[CodeMode()],
    )
    await measure("code mode", Client(code_mode))


if __name__ == "__main__":
    asyncio.run(main())
