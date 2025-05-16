# Package Installation
1. Install [uv](https://docs.astral.sh/uv/)
2. Install package with uv by running `uv sync` in terminal

# Code Execution Sandbox Pulling
1. Go to docker/
2. Get `.env` by coping `.env.example`
3. Run `docker compose -f docker-sandbox-compose.yaml up -d` to init and start sandbox container

# Run Project
1. Edit `.env` and replace the controller_key.
2. Run `uv run app.py` at project root path
