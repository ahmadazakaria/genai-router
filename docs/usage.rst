Quickstart
=========

Activate your project environment and install dependencies::

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

Run the API::

    uvicorn main:app --reload

Send a request::

    curl -X POST localhost:8000/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"llama3","messages":[{"role":"user","content":"Hi"}]}' 

Streaming & the official OpenAI SDK
-----------------------------------

The router speaks **exactly** the same response schema (including streaming
SSE chunks) as the OpenAI API.  That means you can keep using the *official*
`openai` Python package simply by changing the base URL:

.. code-block:: python

   import asyncio, os
   from openai import AsyncOpenAI

   os.environ["OPENAI_API_KEY"] = "dummy"  # router ignores auth
   os.environ["OPENAI_BASE_URL"] = "http://localhost:8000/v1"

   client = AsyncOpenAI()

   async def main():
       stream = await client.chat.completions.create(
           model="llama3",
           messages=[{"role": "user", "content": "Hi"}],
           stream=True,
       )

       async for chunk in stream:
           print(chunk.choices[0].delta.content or "", end="", flush=True)

   asyncio.run(main())

Helper script
~~~~~~~~~~~~~

For convenience the repository ships a ready-to-use CLI that wraps the pattern
above.  Activate the venv and run::

   python scripts/router_chat.py "Tell me a fun fact about llamas"

The script handles interactive prompting when no argument is supplied and
streams the assistant response token-by-token.

Running an Ollama backend without sudo
-------------------------------------

The router forwards requests to an Ollama server listening on
``GENAI_OLLAMA_BASE_URL`` (default ``http://localhost:11434``).  If you
cannot install Ollama system-wide, run it in Docker instead::

    # pull & start Ollama in the background
    docker run -d --name ollama -p 11434:11434 ollama/ollama:latest

    # optional – download a model inside the container
    docker exec -it ollama ollama pull llama3

After the model finishes downloading, the previous *curl* example will return
an assistant response routed through the Dockerised Ollama backend.

To target a remote Ollama instance instead, start the router with::

    export GENAI_OLLAMA_BASE_URL=http://remote-host:11434
    uvicorn main:app --reload 