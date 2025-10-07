# AI Copilot Backend (FastAPI)

This service provides REST endpoints for health checks and a scaffolded chat API intended for future integration with Google Gemini.

Key endpoints:
- GET / and GET /health — basic health checks
- GET /api/config — returns {"gemini_configured": true|false}
- POST /api/chat — accepts chat payload and returns a stubbed response; returns 400 if Gemini API key is not configured

Environment configuration:
- The backend reads the Gemini API key from the environment at request time.
- Required variable for chat: GCP_GEMINI_API_KEY
  - Do not commit secrets or place them in the repo.
  - The value is not logged or returned by any endpoint.
- Optional compatibility: REACT_APP_GEMINI_API_KEY is also checked if present, but GCP_GEMINI_API_KEY is the canonical backend variable.

Payload formats:

POST /api/chat
Request body:
{
  "messages": [
    { "role": "user", "content": "Hello" }
  ],
  "model": "gemini-1.5-pro"
}

Response (stub):
{
  "message": { "role": "assistant", "content": "Hello! Gemini integration is not enabled..." },
  "model": "gemini-1.5-pro",
  "notes": "No external calls performed; SDK integration pending."
}

Notes:
- No external Gemini SDK calls are made yet; this is a safe stub suitable for wiring the frontend.
- CORS is enabled broadly for preview environments; restrict origins in production.
