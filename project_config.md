# 📘 Technical Specification Document – Version 1.0
**Project Name**: LLM Multi-Backend Adapter (OpenAI-Compatible)
**Author**: Ahmad Zakaria  
**Created on**: 2025-06-14  
**Document Version**: 1.0

---

## 1. Objective

The goal of this project is to develop an adapter (smart proxy) that dynamically routes OpenAI-style API requests to multiple backend LLM servers (local or remote), while maintaining compatibility with clients and tools built for the OpenAI API.

---

## 2. Core Features

### 2.1 Multi-backend support
- Local Ollama models (e.g. `llama3`, `mistral`)
- Internal HTTP servers (e.g. MCP)
- Remote enterprise or HuggingFace-hosted models

### 2.2 OpenAI-compatible API
- Supported routes: `/v1/chat/completions`, `/v1/completions`, `/v1/models`, etc.
- Request and response formats fully aligned with OpenAI

### 2.3 Dynamic routing
- Based on model name (e.g. `llama3`, `company-gpt`)
- Configurable via environment variables or YAML/JSON config files

### 2.4 Streaming mode
- SSE-compatible streaming for supported backends
- Auto fallback to standard HTTP when streaming is unsupported

### 2.5 Logging & tracing
- Logs for incoming requests, model used, latency, errors
- Option to anonymize or redact sensitive prompt content

### 2.6 Optional local test interface
- Simple web-based UI to test and debug model responses

---

## 3. Technical Constraints

- Backend in **Python** (preferably FastAPI)
- Must support **async/await**
- Compatible with Python 3.10+
- No mandatory cloud dependencies
- Optional Docker support

---

## 4. Technical Architecture (v1)

```
Client (e.g. LangChain, UI) → [LLM Adapter Proxy] → [Target Backend Model]
```

### Components:
- `router.py`: routing logic
- `handlers/`: per-backend communication handlers (Ollama, HTTP, socket, etc.)
- `schemas/`: OpenAI-compatible request/response Pydantic models
- `config/`: YAML/JSON loader
- `main.py`: FastAPI entry point

---

## 5. Development Roadmap

| Step | Description | Status |
|------|-------------|--------|
| ✅ BB1 | Minimal proxy `/v1/chat/completions` → local Ollama | Done |
| ⏳ BB2 | Add support for MCP or generic HTTP server | In progress |
| ⏳ BB3 | Implement OpenAI-like streaming | To do |
| ⏳ BB4 | Add external config for multi-backend support | To do |
| ⏳ BB5 | Unit tests with mocks | To do |
| ⏳ BB6 | Add Dockerfile & CLI demo mode | To do |

---

## 6. Backlog (v2+ Ideas)

- API Key authentication (mock or real)
- Plugin for local model auto-detection
- Minimal React playground UI
- Direct LangChain / LlamaIndex integration
- Benchmark runner for comparing models
