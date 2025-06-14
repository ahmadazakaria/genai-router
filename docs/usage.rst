Quickstart
=========

Activate your project environment and install dependencies::

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

Run the API::

    uvicorn main:app --reload

Send a request::

    curl -X POST localhost:8000/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"llama3","messages":[{"role":"user","content":"Hi"}]}' 

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