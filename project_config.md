# Project Configuration: GenAI Router

## Project Name
**genai-router**

## Goal
A smart proxy that routes OpenAI-compatible API requests to multiple LLM backends (local or remote) with support for streaming, logging, and flexible configuration.

## Key Technologies
- Python 3.10+
- FastAPI
- Async support
- Ollama / HTTP / Custom backends
- SSE Streaming
- Docker (optional)

## OpenAI-Compatible Routes
- `/v1/chat/completions`
- `/v1/completions`
- `/v1/models`
