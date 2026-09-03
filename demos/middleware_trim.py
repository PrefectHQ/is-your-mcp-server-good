"""what one tool call costs the agent, before and after a response-trimming middleware.

run: uv run demos/middleware_trim.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from prefect_servers import build  # noqa: E402

from fastmcp import Client  # noqa: E402

TOOL = "read_flow_runs_flow_runs_filter_post"
ARGS = {"limit": 5, "sort": "START_TIME_DESC"}


async def cost(label: str, flavor: str) -> None:
    async with Client(build(flavor)) as client:
        result = await client.call_tool(TOOL, ARGS)
    payload = result.structured_content or [c.text for c in result.content if hasattr(c, "text")]
    body = json.dumps(payload)
    print(f"{label:<12} {len(body):>8,} bytes  ~{len(body) // 4:>6,} tokens  for 5 flow runs")


async def main() -> None:
    await cost("raw", "one-to-one")
    await cost("trimmed", "trimmed")


if __name__ == "__main__":
    asyncio.run(main())
