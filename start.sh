#!/usr/bin/env bash
# Start script for Render deployment

# Navigate to project root (should already be there)
cd "$(dirname "$0")"

# Start the FastAPI application with uvicorn
exec uvicorn server.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
