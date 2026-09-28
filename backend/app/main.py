from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.chat import router as chat_router
from app.api.approvals import router as approvals_router
from app.api.master_data import router as master_data_router
from app.api.rag import router as rag_router

app = FastAPI(
    title="Samanvay API — Maharashtra Industry Setup & Approval Assistant",
    description="Deterministic regulatory advisory and approval navigation platform for Maharashtra",
    version="1.0.0"
)

origins = settings.cors_origins_list
if not origins or "*" in origins:
    allow_origins = ["*"]
else:
    allow_origins = origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All API Routers
app.include_router(chat_router)
app.include_router(approvals_router)
app.include_router(master_data_router)
app.include_router(rag_router)

@app.get("/")
def root():
    return {
        "service": "Samanvay (समन्वय) — Maharashtra Industry Setup & Approval Assistant",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs",
        "disclaimer": "This assistant provides preliminary guidance based on available regulatory information. Actual approval requirements may vary based on project-specific conditions."
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "scope": "Maharashtra, India"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
