from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import logging
from pathlib import Path

from .core.config import config
from .core.session_manager import session_manager
from .api.websocket_handler import websocket_handler
from .llm.provider_manager import provider_manager
from .monitoring.self_awareness import self_awareness_monitor
from .audio.speech_processor import speech_processor

# Initialize FastAPI app
app = FastAPI(
    title="Self-Aware Voice Assistant",
    description="Voice-activated AI assistant with self-awareness monitoring",
    version="2.0.0"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    # Mount individual directories to match frontend URL structure
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    app.mount("/components", StaticFiles(directory=str(frontend_path / "components")), name="components")
    app.mount("/services", StaticFiles(directory=str(frontend_path / "services")), name="services")

@app.get("/")
async def read_root():
    """Serve the main frontend page"""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        return FileResponse(frontend_file)
    return {"message": "Self-Aware Voice Assistant API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "active_sessions": session_manager.get_session_count(),
        "api_keys_loaded": {
            "openai": config.has_api_key("openai"),
            "claude": config.has_api_key("claude"),
            "xai": config.has_api_key("xai")
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/session")
async def create_session():
    """Create a new session"""
    session_id = session_manager.create_session()
    return {
        "session_id": session_id,
        "websocket_url": f"/ws/{session_id}"
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_manager.remove_session(session_id)
    return {"message": "Session deleted successfully"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket_handler.handle_connection(websocket, session_id)

@app.get("/providers/status")
async def get_provider_status():
    """Get status of all LLM providers"""
    return {
        "providers": provider_manager.get_provider_status()
    }

@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    logger.info("Initializing Self-Aware Voice Assistant components...")
    
    # Initialize LLM provider manager
    await provider_manager.initialize()
    
    # Initialize self-awareness monitor
    if await self_awareness_monitor.initialize():
        # Start monitoring in background
        import asyncio
        asyncio.create_task(self_awareness_monitor.start_monitoring())
    
    # Initialize speech processor
    await speech_processor.initialize()
    
    logger.info("All components initialized successfully")

if __name__ == "__main__":
    logger.info("Starting Self-Aware Voice Assistant")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )