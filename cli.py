"""GenAI Router command-line interface.

Usage examples::

    # Run API server (uvicorn)
    genai-router run-server --host 0.0.0.0 --port 8080

    # Quick chat completion call to the server
    genai-router chat --model llama3 "Hello!"
"""

from __future__ import annotations

import json
import sys
from typing import Optional

import httpx
import typer

app = typer.Typer(add_completion=False, name="genai-router")

DEFAULT_SERVER = "http://localhost:8000"


@app.command()
def run_server(
    host: str = typer.Option("0.0.0.0", help="Bind address"),
    port: int = typer.Option(8000, help="Port number"),
    reload: bool = typer.Option(False, help="Enable autoreload (dev only)"),
):
    """Launch the FastAPI application using Uvicorn."""
    import uvicorn  # local import to avoid pulling in server deps for chat cmd

    uvicorn.run("main:app", host=host, port=port, reload=reload)


@app.command()
def chat(
    message: str = typer.Argument(..., help="Prompt for the assistant"),
    model: str = typer.Option("llama3", "--model", "-m", help="Model name"),
    server: str = typer.Option(DEFAULT_SERVER, "--server", "-s", help="Server base URL"),
    stream: bool = typer.Option(False, "--stream", help="Enable streaming"),
):
    """Send a chat completion request to a running GenAI Router instance."""

    payload = {
        "model": model,
        "stream": stream,
        "messages": [{"role": "user", "content": message}],
    }

    url = f"{server.rstrip('/')}/v1/chat/completions"
    with httpx.Client(timeout=30.0) as client:
        if stream:
            with client.stream("POST", url, json=payload) as resp:
                for line in resp.iter_lines():
                    if line:
                        # Each line is already JSON chunk prefixed with data:
                        print(line.lstrip("data: "))
        else:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":  # pragma: no cover
    app() 