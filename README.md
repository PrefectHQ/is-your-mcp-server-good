# Is Your MCP Server Good?

These are the examples from [Is Your MCP Server Good? Building MCP Servers for
Agents](https://luma.com/sugswsfy). They use the [Prefect API](https://prefect.io)
to explore how tool design affects the information an agent has to read and the
work it can accomplish.

You can compare an MCP generated from OpenAPI with a smaller, hand-written
server, try code mode, and see what happens when middleware removes empty fields
from responses. The examples use [FastMCP](https://gofastmcp.com). For background,
see [Stop converting your REST APIs to MCP](https://jlowin.dev/blog/stop-converting-rest-apis-to-mcp).

## Try the examples

Install [uv](https://docs.astral.sh/uv/), then start a local Prefect server:

```sh
uvx prefect server start
```

Leave it running. In another terminal, compare the tool listings:

```sh
uvx --from git+https://github.com/PrefectHQ/is-your-mcp-server-good context-tax
```

To compare a response before and after trimming nulls and empty collections:

```sh
uvx --from git+https://github.com/PrefectHQ/is-your-mcp-server-good middleware-trim
```

The examples connect to `http://localhost:4200/api`. Run a few Prefect flows
against that server first so the response comparison has data to work with.

## What the examples compare

| server | approach |
| --- | --- |
| `one-to-one` | Generates a tool for each operation in the Prefect OpenAPI spec. |
| `trimmed` | Uses the generated tools, with middleware that removes null values and empty collections from responses. |
| `code-mode` | Wraps the generated server in FastMCP's `CodeMode` transform, exposing three tools for discovering and calling its operations. |
| `prefect-designed` | Runs the separately maintained [Prefect MCP server](https://github.com/PrefectHQ/prefect-mcp-server), whose tools are written for common Prefect workflows. |

`context-tax` reports the number of tools and the size of their serialized
listing for the generated, hand-written, and code-mode servers. `middleware-trim`
compares the serialized response to a request for five flow runs.

Here is output recorded on September 3, 2026:

```text
one-to-one      187 tools  1,650,912 bytes  ~412,728 tokens
designed         14 tools     37,008 bytes  ~  9,252 tokens
code mode         3 tools      2,362 bytes  ~    590 tokens

raw            10,312 bytes  ~2,578 tokens  for 5 flow runs
trimmed         6,444 bytes  ~1,611 tokens  for 5 flow runs
```

The scripts estimate tokens by dividing the serialized length by four. These
numbers describe the listings and responses in that run; they aren't a bill for
an agent session. Results vary with package versions, the API schema, and your
flow data. With code mode, the agent retrieves further schemas as it works, so
the initial listing doesn't include everything it may read later.

## Try them with an agent

The [`.mcp.json`](.mcp.json) file configures all four servers as stdio commands.
Clone this repository and open it in Claude Code, or adapt those entries for
your MCP client. Enable one server at a time to compare how it handles the same
request, such as “Why did my last flow run fail?” You'll need a failed run in the
local Prefect server for that example.

Read the agent's tool calls and answer alongside the size measurements. Check
whether it found the relevant run, obtained enough evidence to explain the
failure, and gave you an answer you could use. A smaller listing can help, but
it doesn't establish that the tools are useful or the answer is correct.

The generated servers cache the OpenAPI spec under
`~/.cache/mcp-server-demos`. After a successful fetch, they can start from that
copy if the API is unavailable. Tool calls still need the API running.

## License

[Apache 2.0](LICENSE)
