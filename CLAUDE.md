# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A CLI application for interactive chat with Claude AI models via the Anthropic API. It demonstrates the Model Context Protocol (MCP) by implementing a client-server document management system with tool integration. Based on Anthropic's Introduction to Model Context Protocol course.

## Setup & Running

```bash
# Install dependencies (uv recommended)
uv venv && source .venv/bin/activate
uv pip install -e .

# Required: copy .env.example to .env and fill in ANTHROPIC_API_KEY and CLAUDE_MODEL
cp .env.example .env

# Run the app
uv run main.py

# Run with additional custom MCP servers
uv run main.py <extra_server.py> ...

# Inspect the MCP server
mcp dev mcp_server.py
```

No linting, type checking, or test suite is currently configured.

## Architecture

The application has two parallel tracks that join at runtime:

**MCP Server** (`mcp_server.py`) — A FastMCP server that exposes document management as MCP tools (`list_all_docs`, `read_doc_contents`, `edit_document`), resources (`docs://documents/{doc_id}`), and prompts (`format`). Runs as a subprocess.

**Client stack** (called from `main.py`):
- `mcp_client.py` (`MCPClient`) — Wraps stdio-based MCP protocol communication. One instance connects to `mcp_server.py` (the `doc_client`); additional instances can connect to custom servers passed as CLI args.
- `core/tools.py` (`ToolManager`) — Aggregates tools from all connected MCP clients and routes `call_tool()` calls to the right client.
- `core/claude.py` (`Claude`) — Thin Anthropic SDK wrapper (`chat()`, `text_from_message()`).
- `core/chat.py` (`Chat`) — Base class implementing the tool-use loop: send message → detect `tool_use` blocks → execute via `ToolManager` → append result → continue until no more tool calls.
- `core/cli_chat.py` (`CliChat`) — Extends `Chat`. Intercepts user input to handle `/command` syntax (fetches MCP prompts) and `@doc_id` syntax (injects resource content as context before calling the model).
- `core/cli.py` (`CliApp`) — prompt-toolkit REPL with tab completion for `/` (commands) and `@` (document IDs), key bindings, and in-memory history.

**Data flow for a user query:**
```
User input → CliApp → CliChat._process_query()
  → resolve @resources / /commands
  → Chat.run() → Claude.chat() → tool_use loop via ToolManager → MCPClient → mcp_server
```

## Key Conventions

- **Async throughout** — all I/O uses `async/await`; top-level entry uses `asyncio.run()`.
- **Environment config** — `ANTHROPIC_API_KEY` and `CLAUDE_MODEL` loaded from `.env` via `python-dotenv`; validated at startup in `main.py`.
- **MCP client lifecycle** — `MCPClient` is an async context manager; `main.py` uses a shared `AsyncExitStack` to manage all client lifetimes together.
- **Tool routing** — `ToolManager` maps tool names back to the originating `MCPClient` so `call_tool()` always reaches the right server.
