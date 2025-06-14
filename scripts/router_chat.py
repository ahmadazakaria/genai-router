#!/usr/bin/env python
"""Chat with local genai-router powered by Ollama.

This script sends a chat completion request to the router using the **same schema**
as OpenAI's API, so you can keep using the official `openai` Python SDK merely by
changing the `base_url`.

Setup
-----
1.  Make sure the router is running locally.  With *Docker Compose*::

        docker compose up --build router ollama

    (or run the FastAPI app manually with `uvicorn main:app --reload`.)

2.  Export two env-vars or add them to your `.env` file::

        # Required by the OpenAI SDK, but the router ignores authentication.
        OPENAI_API_KEY="dummy"

        # Where the router is reachable.  By default uvicorn in compose
        # publishes on host port 8000.
        OPENAI_BASE_URL="http://localhost:8000/v1"

Usage
-----
    python scripts/router_chat.py "Tell me a dad joke"

If you omit the prompt on the command line you will be prompted interactively.
"""
from __future__ import annotations

import asyncio
import os
import sys
from typing import List

from dotenv import load_dotenv  # type: ignore
from openai import AsyncOpenAI

DEFAULT_MODEL = "llama3"


def _get_client() -> AsyncOpenAI:
    """Return an `AsyncOpenAI` instance configured for the local router."""
    api_key = os.getenv("OPENAI_API_KEY", "dummy")
    base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")
    return AsyncOpenAI(api_key=api_key, base_url=base_url)


def _build_messages(user_prompt: str) -> List[dict[str, str]]:
    return [
        {"role": "system", "content": "You are a helpful assistant running on llama3."},
        {"role": "user", "content": user_prompt},
    ]


async def run_chat(prompt: str, model: str = DEFAULT_MODEL) -> None:
    client = _get_client()
    completion = await client.chat.completions.create(
        model=model,
        messages=_build_messages(prompt),
        temperature=0.7,
        stream=True,  # leverage streaming capabilities of the router
    )

    # The OpenAI SDK yields `ChatCompletionChunk` objects when streaming.
    async for chunk in completion:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)

    print()  # final newline


async def main() -> None:
    load_dotenv()

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Prompt › ").strip()
        if not prompt:
            print("Empty prompt, exiting.")
            return

    await run_chat(prompt)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.") 