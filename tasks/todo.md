# GenAI Router – TODO Breakdown

## Phase 1 – Core Proxy
- [ ] Build `/v1/chat/completions` handler
- [ ] Add streaming support flag
- [ ] Develop Ollama handler interface
- [ ] Validate Pydantic schemas

## Phase 2 – Multi-backend Logic
- [ ] Add config reader
- [ ] Route model selection based on config
- [ ] Add HTTP backend support

## Phase 3 – Observability & Testing
- [ ] Structured logging & trace IDs
- [ ] Unit tests for each component
- [ ] Error handling in router

## Phase 4 – Packaging
- [ ] Dockerfile
- [ ] CLI demo script
- [ ] Usage documentation
