from fastapi import APIRouter
from backend.app.api.endpoints import (
    voice, conversation, ledger, entities, analytics, reminders, queries, documents, benchmark
)

api_router = APIRouter()
api_router.include_router(voice.router)
api_router.include_router(conversation.router)
api_router.include_router(ledger.router)
api_router.include_router(entities.router)
api_router.include_router(analytics.router)
api_router.include_router(reminders.router)
api_router.include_router(queries.router)
api_router.include_router(documents.router)
api_router.include_router(benchmark.router)
