from typing import List, Literal, Optional

import os
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
app = FastAPI(
    title="AI Copilot Backend",
    description="FastAPI backend for AI Copilot. Provides health check and chat APIs.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Service health and status endpoints"},
        {"name": "config", "description": "Runtime configuration discovery (no secrets)"},
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


def _get_gemini_api_key() -> Optional[str]:
    """
    Internal helper to get the Gemini API key from environment at request time.
    Never log or cache the key; return as-is or None if not set.
    """
    # Read on each request; do not read at import time
    key = os.environ.get("GCP_GEMINI_API_KEY") or os.environ.get("REACT_APP_GEMINI_API_KEY")
    # Note: we also check REACT_APP_GEMINI_API_KEY in case environments use that name,
    # but GCP_GEMINI_API_KEY is the official variable for backend.
    if key is not None and key.strip() == "":
        return None
    return key


# ---------- Models for Chat API (scaffolding for future Gemini integration) ----------

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Role of the message author.")
    content: str = Field(..., description="Message text content.")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Ordered list of chat messages.")
    model: Optional[str] = Field(
        default="gemini-1.5-pro",
        description="Gemini model to use. Placeholder only; no external calls yet.",
    )


class ChatResponse(BaseModel):
    message: ChatMessage = Field(..., description="Assistant response message.")
    model: str = Field(..., description="Model identifier used for the response.")
    notes: Optional[str] = Field(
        default=None,
        description="Extra notes about the response generation (for debugging/scaffolding).",
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


# PUBLIC_INTERFACE
@app.get(
    "/api/config",
    tags=["config"],
    summary="Configuration status (no secrets)",
    description="Returns whether the Gemini API is configured. Does not return any secrets.",
    responses={
        200: {
            "description": "Configuration status returned",
            "content": {"application/json": {"example": {"gemini_configured": True}}},
        }
    },
)
def get_config():
    """
    Report configuration status for Gemini.

    Returns:
        dict: {"gemini_configured": bool} indicating if GCP_GEMINI_API_KEY is set.
    """
    configured = _get_gemini_api_key() is not None
    return {"gemini_configured": configured}


# PUBLIC_INTERFACE
@app.post(
    "/api/chat",
    tags=["chat"],
    summary="Chat with Gemini (stub)",
    description=(
        "Accepts chat messages and returns a stubbed response. "
        "If the Gemini API key is not configured via environment variable GCP_GEMINI_API_KEY, "
        "returns 400 with a helpful error. This endpoint is scaffolded for future integration "
        "with the Google Generative AI SDK; no external calls are made yet."
    ),
    responses={
        200: {
            "description": "Stubbed chat response",
            "content": {
                "application/json": {
                    "example": {
                        "message": {"role": "assistant", "content": "Hello! This is a stubbed response."},
                        "model": "gemini-1.5-pro",
                        "notes": "No external calls performed; SDK integration pending.",
                    }
                }
            },
        },
        400: {
            "description": "Gemini API key not configured",
            "content": {"application/json": {"example": {"error": "Gemini API key not configured"}}},
        },
    },
)
def chat(request: ChatRequest = Body(...)) -> ChatResponse:
    """
    Chat endpoint stub for Gemini integration.

    Parameters:
        request (ChatRequest): JSON body with messages and optional model.

    Returns:
        ChatResponse: A stubbed assistant message using the requested or default model.

    Raises:
        HTTPException 400: If GCP_GEMINI_API_KEY is not set in the environment.
    """
    api_key = _get_gemini_api_key()
    if not api_key:
        # Do not log or expose the key; return a clear, user-friendly error
        raise HTTPException(status_code=400, detail="Gemini API key not configured")

    # Placeholder for future Google Generative AI SDK integration:
    # - Initialize client with api_key
    # - Send request.messages to the selected model
    # - Stream/return response
    #
    # For now, echo a basic helpful stub.
    last_user = next((m for m in reversed(request.messages) if m.role == "user"), None)
    assistant_text = (
        "Hello! Gemini integration is not enabled in this preview. "
        "This is a stubbed response. Your last message was: "
        f"\"{last_user.content}\"" if last_user else
        "Hello! Gemini integration is not enabled in this preview. This is a stubbed response."
    )

    return ChatResponse(
        message=ChatMessage(role="assistant", content=assistant_text),
        model=request.model or "gemini-1.5-pro",
        notes="No external calls performed; SDK integration pending.",
    )
