from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.orders import router
from app.core.config import settings

app = FastAPI(title="Servis za narudžbe", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=["GET", "POST", "PATCH"], allow_headers=["Content-Type"])
app.include_router(router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "gemini_configured": bool(settings.gemini_api_key)}
