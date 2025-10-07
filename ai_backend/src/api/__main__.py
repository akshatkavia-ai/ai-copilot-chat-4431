"""
Module entrypoint to run the FastAPI app with Uvicorn.

Usage:
    python -m src.api
This will bind to 0.0.0.0:3001 so the preview proxy can reach the service.
"""

from uvicorn import run as uvicorn_run

# Import app from main module
from src.api.main import app  # noqa: E402


# PUBLIC_INTERFACE
def main():
    """Run the FastAPI application with Uvicorn on 0.0.0.0:3001."""
    # Host must be 0.0.0.0 in containerized/preview environments
    uvicorn_run(app, host="0.0.0.0", port=3001, log_level="info")


if __name__ == "__main__":
    main()
