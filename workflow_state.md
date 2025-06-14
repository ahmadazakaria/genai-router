# Workflow State

## Current Status
We are starting from scratch and building a fully functional, modular, and testable GenAI Router.

## Milestones
- [ ] BB1: Basic Proxy `/v1/chat/completions` to Ollama
- [ ] BB2: Support for internal MCP or generic HTTP LLM backends
- [ ] BB3: Implement SSE streaming responses
- [ ] BB4: Config file loader for multi-backend routing
- [ ] BB5: Unit tests for routing and handler logic
- [ ] BB6: CLI and Docker packaging

## In Progress
- Project scaffolding and core route implementation

## Rules
- Use `async def` with FastAPI
- Mirror OpenAI API structure
- Modular design: router, handlers, schemas, config
- Local-first approach, no cloud-only deps
- YAML/JSON model-to-backend routing via config

## Completed Log
- Project folder initialized
- Base FastAPI app with `/v1/chat/completions` added
- `.cursor/rules/` structure created
