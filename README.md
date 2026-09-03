# is your mcp server good?

the demos behind the webinar [Is Your MCP Server Good? Building MCP Servers for
Agents](https://luma.com/sugswsfy): one REST API, the [Prefect](https://prefect.io)
API, served four ways with [FastMCP](https://gofastmcp.com), so the cost of each
design shows up as a number an agent would pay. the argument it illustrates is
[stop converting your REST APIs to MCP](https://jlowin.dev/blog/stop-converting-rest-apis-to-mcp).

## what's here

four servers over the same API, and two scripts that measure them:

| server | what it is |
| --- | --- |
| `one-to-one` | `FastMCP.from_openapi` over the Prefect spec; every operation is a tool |
| `trimmed` | the same, plus a middleware that drops null and empty fields from responses |
| `code-mode` | the same, behind a `CodeMode` transform; the agent sees three meta-tools |
| `prefect-designed` | the hand-written [prefect-mcp-server](https://github.com/PrefectHQ/prefect-mcp-server), run via `uvx --from prefect-mcp prefect-mcp-server` |

```sh
uvx prefect server start                                                       # a local prefect api at localhost:4200
uvx --from git+https://github.com/PrefectHQ/is-your-mcp-server-good context-tax       # tools and listing size, three servers
uvx --from git+https://github.com/PrefectHQ/is-your-mcp-server-good middleware-trim   # one tool call, before and after the middleware
```

measured 2026-09-03, token counts estimated as bytes divided by four:

```
one-to-one      187 tools  1,650,912 bytes  ~412,728 tokens
designed         14 tools     37,008 bytes  ~  9,252 tokens
code mode         3 tools      2,362 bytes  ~    590 tokens

raw            10,312 bytes  ~2,578 tokens  for 5 flow runs
trimmed         6,444 bytes  ~1,611 tokens  for 5 flow runs
```

all four servers are configured in [`.mcp.json`](.mcp.json) as `uvx` commands, so
`claude` launched from a clone can attach to any of them, and the same entries can
be pasted into any other client's config. the local Prefect api needs some
flow runs in it before the "why did my last run fail" prompt has anything to find.

## design

- **one domain, four servers** — every point about tool design is the same API
  under a different transform, so there is one mental model and one setup.
- **measure the listing, not the vibe** — the numbers are the serialized
  `tools/list` result, the thing an agent pays for before the user asks anything.
- **the designed server is real** — prefect-mcp-server is built through evals on
  every pull request; it is the customer story, not a toy.
- **the spec is cached** — the servers fetch the OpenAPI spec from the running
  api and keep a copy under `~/.cache/mcp-server-demos`, so they start even when
  the api is down; tool calls still need it up.

## license

[Apache 2.0](LICENSE)
