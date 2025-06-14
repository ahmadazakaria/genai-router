#!/usr/bin/env python
"""Simple helper script to test that your OpenAI API key is working.

Usage:
1.  Add your key to a `.env` file at the project root::

        OPENAI_API_KEY="sk-..."

    (Quotes optional.)

2.  Install dependencies (inside the project virtual-env)::

        pip install -r requirements.txt

3.  Run the script::

        python scripts/openai_chat.py "What is the capital of France?"

If everything is configured correctly you should see the assistant's answer printed
on stdout.
"""
from __future__ import annotations

import asyncio
import os
import sys
from typing import List
import time

from dotenv import load_dotenv  # type: ignore
from openai import AsyncOpenAI, RateLimitError, APIConnectionError


def _get_api_key() -> str:
    """Read ``OPENAI_API_KEY`` from the environment and fail fast if missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Environment variable OPENAI_API_KEY is not set.\n"
                           "Create a .env file with `OPENAI_API_KEY=...` or export it before running.")
    return api_key


def _build_messages(user_prompt: str) -> List[dict[str, str]]:
    """Return a minimal chat history for the request."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_prompt},
    ]


async def main() -> None:
    """Entry-point; send the prompt given on the CLI to OpenAI and print the reply."""
    load_dotenv(override=False)  # load variables from .env if present

    if len(sys.argv) < 2:
        print("Usage: python scripts/openai_chat.py <prompt>")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])

    client = AsyncOpenAI(api_key=_get_api_key())

    max_retries = 3
    backoff = 2  # seconds, will be multiplied each retry

    for attempt in range(1, max_retries + 1):
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=_build_messages(prompt),
                temperature=0.7,
            )

            message = response.choices[0].message.content.strip()
            print("Assistant:", message)
            break  # Success, exit loop

        except RateLimitError as e:
            if attempt == max_retries:
                print("[ERROR] OpenAI API rate-limit/insufficient-quota: ", e.message)
                print("       Check your plan & billing at https://platform.openai.com/account/usage")
                sys.exit(1)
            wait = backoff * attempt
            print(f"Rate limited. Retrying in {wait}s… (attempt {attempt}/{max_retries})")
            await asyncio.sleep(wait)

        except APIConnectionError as e:
            if attempt == max_retries:
                print("[ERROR] Network error while contacting OpenAI API:", e.message)
                sys.exit(1)
            wait = backoff * attempt
            print(f"Network error. Retrying in {wait}s… (attempt {attempt}/{max_retries})")
            await asyncio.sleep(wait)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user." ) 