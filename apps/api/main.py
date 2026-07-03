from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routes import pid
from apps.api.routes import rca

from apps.api.routes import (
    ask,
    assets,
    compliance,
    dashboard,
    documents,
    knowledge_graph,
    maintenance,
)
from apps.api.services.data_loader import clear_data_cache, get_file_status


app = FastAPI(
    title="PlantMind AI API",
    description="Backend API for Industrial Asset and Operations Intelligence demo.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(dashboard.router)
app.include_router(assets.router)
app.include_router(documents.router)
app.include_router(compliance.router)
app.include_router(maintenance.router)
app.include_router(knowledge_graph.router)
app.include_router(ask.router)
app.include_router(pid.router)
app.include_router(rca.router)

@app.get("/", tags=["System"])
def root():
    return {
        "message": "PlantMind AI API is running",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "PlantMind AI API",
    }


@app.get("/status/files", tags=["System"])
def file_status():
    return get_file_status()


@app.post("/admin/reload-cache", tags=["System"])
def reload_cache():
    clear_data_cache()

    return {
        "status": "cache_cleared",
        "message": "Data cache cleared. Next request will reload JSON files."
    }