#!/usr/bin/env bash
# Rebuild and (re)launch the docker-compose stack.
# Usage: ./scripts/reload_stack.sh [service ...]
# If no services are passed, the entire stack is rebuilt.

set -euo pipefail

COMPOSE_FILE="compose.yaml"

# Pick docker compose command: prefer `docker compose`, fallback to `docker-compose`
if docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
else
  echo "❌ Neither 'docker compose' nor 'docker-compose' found. Please install Docker Compose." >&2
  exit 1
fi

if [[ "$#" -eq 0 ]]; then
  echo "🛑 Stopping stack ..."
  $DC -f "$COMPOSE_FILE" down --remove-orphans

  # Remove any lingering containers that were started outside this compose stack
  echo "🧹 Cleaning stray containers with conflicting names..."
  for svc in $($DC -f "$COMPOSE_FILE" config --services); do
    docker rm -f "$svc" 2>/dev/null || true
  done

  # Also remove containers that have explicit container_name fields
  for cname in genai-router ollama; do
    docker rm -f "$cname" 2>/dev/null || true
  done

  echo "🔄 Rebuilding all services..."
  $DC -f "$COMPOSE_FILE" build --pull
  $DC -f "$COMPOSE_FILE" up -d
else
  echo "🛑 Stopping containers: $*"
  $DC -f "$COMPOSE_FILE" stop "$@" || true
  $DC -f "$COMPOSE_FILE" rm -f "$@" || true

  echo "🔄 Rebuilding selected services: $*"
  $DC -f "$COMPOSE_FILE" build --pull "$@"
  $DC -f "$COMPOSE_FILE" up -d --no-deps "$@"
fi

# Show status
sleep 1
$DC -f "$COMPOSE_FILE" ps 