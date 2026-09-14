from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.router import api_router
from backend.app.database.session import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables cleanly without auto-populating synthetic data
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Bilingual Voice & Text Bookkeeping Intelligence Platform for Small Businesses",
    lifespan=lifespan
)

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "engine": "NLP-Khata-Deterministic-v1"}
