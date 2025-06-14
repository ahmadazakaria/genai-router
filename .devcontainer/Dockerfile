FROM mcr.microsoft.com/devcontainers/python:3.11

# Install extra tools
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Pre-create virtual environment path to speed up `postCreateCommand`
ENV VENV_PATH=/workspace/.venv

CMD ["bash"] 