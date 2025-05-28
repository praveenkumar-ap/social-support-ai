# Makefile for one-command build & demo

.PHONY: all clean llm api ui up down logs

# Default: clean slate then bring everything up
all: clean llm api ui up

# Remove all containers, images, volumes
clean:
	docker compose down --rmi all --volumes --remove-orphans

# Build & start LLM (auto-pulls model)
llm:
	docker compose up -d --build llm

# Build & start API
api:
	docker compose up -d --build api

# Start UI (bind-mount picks up code changes)
ui:
	docker compose up -d ui

# Bring up the entire stack (db, chromadb, llm, api, ui)
up:
	docker compose up -d

# Tear down just in case
down:
	docker compose down

# Show combined logs
logs:
	docker compose logs -f