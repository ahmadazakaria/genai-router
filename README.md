# GenAI Router

![CI](https://github.com/ahmadazakaria/genai-router/actions/workflows/ci.yml/badge.svg)

The goal of this project is to develop an adapter (smart proxy) that dynamically routes OpenAI-style API requests to multiple backend LLM servers (local or remote), while maintaining compatibility with clients and tools built for the OpenAI API.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install  # activate git hooks
```

Run tests:

```bash
pytest -q
```

## CLI

Install extra requirement ``typer`` already shipped in requirements. Example::

    source .venv/bin/activate
    pip install -r requirements.txt

    # run server
    python -m cli run-server --reload

    # quick chat request
    python -m cli chat --model llama3 "Hello!"

## Docker

Build and run::

    docker build -t genai-router .  # image bundles its own virtualenv
    docker run -p 8000:8000 genai-router

### Ollama backend in Docker (no sudo)

If you cannot install **Ollama** on the host machine run it as a container::

    docker run -d --name ollama -p 11434:11434 ollama/ollama:latest

    # pull a model inside the container
    docker exec -it ollama ollama pull llama3

The GenAI Router will automatically forward to this backend at
``http://localhost:11434``.

## Docker Compose

Instead of managing containers manually you can use **docker compose**::

    # build + start everything (router + ollama) in background
    docker compose up --build -d

    # or use helper script (rebuild changed services)
    ./scripts/reload_stack.sh             # rebuild all
    ./scripts/reload_stack.sh router      # rebuild only router image

The router container automatically depends on the `ollama` service and
talks to it via the internal service name.  The Compose file mounts a
persistent volume `ollama-data` at `/root/.ollama`, so downloaded models
survive container rebuilds.
