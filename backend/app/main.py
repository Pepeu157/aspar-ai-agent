from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.requests import router as requests_router
from app.core.config import settings

app = FastAPI(
    title="ASPAR AI Agent API",
    version="0.1.0",
    description="API local de apoio à análise de solicitações de audiência com dados sintéticos.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(requests_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aspar-ai-agent-api"}
