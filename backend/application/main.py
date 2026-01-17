"""
FastAPI Main Application - Application Layer

Ponto de entrada da API com suporte a WebSocket.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from domain.database import init_db
from application.routes import upload, status, export, auth, websocket, projects
from application.websocket import manager

# Criar aplicação FastAPI
app = FastAPI(
    title="IsoMix Studio API",
    description="API para separação de fontes de áudio com IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas REST
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(projects.router, prefix="/api", tags=["Projects"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(status.router, prefix="/api", tags=["Status"])
app.include_router(export.router, prefix="/api", tags=["Export"])

# Registrar rotas WebSocket
app.include_router(websocket.router, tags=["WebSocket"])


@app.on_event("startup")
async def startup_event():
    """Inicializar banco de dados ao iniciar"""
    init_db()
    print("✅ Banco de dados inicializado")
    print("🔌 WebSocket pronto em /ws/project/{project_id}")


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "IsoMix Studio API",
        "status": "running",
        "version": "1.0.0",
        "websocket": "/ws/project/{project_id}",
    }


@app.get("/health")
async def health():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "websocket_connections": manager.get_connection_count(),
    }

