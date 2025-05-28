#!/usr/bin/env bash
set -e

# Start Ollama server in the background
ollama serve &

# Wait until the server responds
echo "⏳ Waiting for Ollama to start…"
until curl -s localhost:11434/models >/dev/null; do
  sleep 1
done
echo "✅ Ollama is up."

# Pull the model if missing
MODEL="${OLLAMA_MODEL:-gemma:2b}"
if ! ollama list | grep -q "$MODEL"; then
  echo "⏬ Pulling $MODEL…"
  ollama pull "$MODEL"
else
  echo "✔ Model $MODEL already present."
fi

# Bring the server to foreground
fg %1
