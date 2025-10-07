from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# PUBLIC_INTERFACE
app = FastAPI(
    title="AI Copilot Backend",
    description="FastAPI backend for AI Copilot. Provides health check and chat APIs.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Service health and status endpoints"},
        {"name": "chat", "description": "Endpoints for chat interactions with the LLM"},
    ],
)

# Allow all origins for preview environment; in production restrict as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Preview proxy uses different hostnames
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check (root)", include_in_schema=True)
def root_health_check():
    """
    This is a simple health check endpoint at the root path.
    Returns 200 OK with a simple JSON payload when the service is healthy.

    Returns:
        dict: A JSON object containing a health message.
    """
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Returns service health status for monitoring/proxy checks.",
)
def health_check():
    """
    Health endpoint explicitly at /health for proxy checks.

    Returns:
        dict: Health status payload with service and status fields.
    """
    return {"service": "ai-backend", "status": "ok"}
