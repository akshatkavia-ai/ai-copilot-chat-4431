import os
from typing import List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="AI Copilot Backend",
    description="Backend API for the AI Copilot application, powered by Gemini.",
    version="1.0.0",
)

# Set up CORS - relaxed for localhost development
# In production, restrict to actual frontend domain
origins = [
    "http://localhost:3000",
    "https://vscode-internal-41620-beta.beta01.cloud.kavia.ai:3000",  # Frontend preview origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# --- Pydantic Models ---


class ChatMessage(BaseModel):
    """A single message in the chat history."""

    role: str  # 'user' or 'assistant' ('model' in gemini)
    content: str


class ChatRequest(BaseModel):
    """Request model for the /chat endpoint."""

    messages: List[ChatMessage]
    session_id: Optional[
        str
    ] = None  # Not used in this implementation, but included for future use


class ChatResponse(BaseModel):
    """Response model for the /chat endpoint."""

    reply: str
    model: str
    usage: Optional[dict] = None  # Placeholder for usage data


# --- API Endpoints ---


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint to ensure the server is running."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Receives a list of chat messages and returns a response from the Gemini model.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is missing.")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GEMINI_API_KEY is missing.",
                "hint": "Set GEMINI_API_KEY in backend .env or environment."
            },
        )

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"An error occurred during genai.configure: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Error configuring Gemini API: {str(e)}",
                "hint": "Check API key validity."
            }
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    model = genai.GenerativeModel(model_name)

    # The Gemini API expects roles to be 'user' and 'model'.
    # We'll map 'assistant' to 'model' for the conversation history.
    conversation_history = [
        {"role": msg.role if msg.role != "assistant" else "model", "parts": [msg.content]}
        for msg in request.messages
    ]

    try:
        response = model.generate_content(conversation_history)

        # Ensure the response has content before accessing it
        if not response.parts:
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": "Received an empty response from the AI model.",
                    "hint": "The model may have blocked the response or encountered an issue."
                }
            )

        reply_content = response.text

        return ChatResponse(
            reply=reply_content,
            model=model_name,
            # usage data might be available in response.usage_metadata depending on API version
            usage=(
                response.usage_metadata
                if hasattr(response, "usage_metadata")
                else None
            ),
        )
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred while calling the Gemini API: {e}")
        # Return structured error JSON
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"An error occurred while processing your request: {str(e)}",
                "hint": "Check backend logs and Gemini API status."
            },
        )
