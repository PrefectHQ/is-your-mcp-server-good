"""the same prefect api, served three ways. pick one by name on the command line.

  uv run demos/prefect_servers.py one-to-one   # every rest endpoint is a tool
  uv run demos/prefect_servers.py trimmed      # same, but a middleware drops nulls before the agent sees them
  uv run demos/prefect_servers.py code-mode    # same tools behind search / get_schema / execute

each runs over stdio so claude code or pi can attach to it (see .mcp.json).
"""

import json
import sys
from pathlib import Path
from typing import Any

import httpx2

from fastmcp import FastMCP
from fastmcp.experimental.transforms.code_mode import CodeMode
from fastmcp.server.middleware import Middleware, MiddlewareContext

PREFECT_API = "http://localhost:4200/api"


def _dense(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _dense(v) for k, v in value.items() if v is not None and v != [] and v != {}}
    if isinstance(value, list):
        return [_dense(v) for v in value]
    return value


class DropNulls(Middleware):
    """the rest api returns every field the schema has. the agent only needs the ones with values."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        result = await call_next(context)
        if result.structured_content:
            result.structured_content = _dense(result.structured_content)
            result.content = []
        return result


SPEC_CACHE = Path(__file__).with_name("prefect-openapi.json")


def load_spec() -> dict[str, Any]:
    try:
        spec = httpx2.get(f"{PREFECT_API}/openapi.json", timeout=5).json()
    except httpx2.HTTPError:
        if not SPEC_CACHE.exists():
            raise SystemExit(f"prefect is not running at {PREFECT_API} and no cached spec at {SPEC_CACHE}")
        return json.loads(SPEC_CACHE.read_text())
    SPEC_CACHE.write_text(json.dumps(spec))
    return spec


def build(flavor: str) -> FastMCP:
    spec = load_spec()
    client = httpx2.AsyncClient(base_url=PREFECT_API)
    match flavor:
        case "one-to-one":
            return FastMCP.from_openapi(openapi_spec=spec, client=client, name="prefect (one-to-one)")
        case "trimmed":
            server = FastMCP.from_openapi(openapi_spec=spec, client=client, name="prefect (trimmed)")
            server.add_middleware(DropNulls())
            return server
        case "code-mode":
            return FastMCP.from_openapi(
                openapi_spec=spec, client=client, name="prefect (code mode)", transforms=[CodeMode()]
            )
    raise SystemExit(f"unknown flavor {flavor!r}; use one-to-one, trimmed, or code-mode")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "one-to-one").run()
