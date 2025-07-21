import uuid
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.websocket = None
        self.user_data = {}
        self.conversation_history = []
        self.current_provider = None
        self.current_model = None
        self.audio_settings = {}
        
    def update_activity(self):
        self.last_activity = datetime.now()
    
    def add_conversation_turn(self, user_message: str, assistant_response: str, provider: str, model: str):
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'assistant': assistant_response,
            'provider': provider,
            'model': model
        })
        # Keep only last 10 turns to manage memory
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.logger = logging.getLogger(__name__)
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task to clean up expired sessions"""
        async def cleanup():
            while True:
                await asyncio.sleep(300)  # Check every 5 minutes
                await self.cleanup_expired_sessions()
        
        self._cleanup_task = asyncio.create_task(cleanup())
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = Session(session_id)
        self.logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session:
            session.update_activity()
        return session
    
    def remove_session(self, session_id: str):
        """Remove a session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.websocket:
                asyncio.create_task(session.websocket.close())
            del self.sessions[session_id]
            self.logger.info(f"Removed session: {session_id}")
    
    async def cleanup_expired_sessions(self):
        """Remove sessions that haven't been active for over an hour"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.last_activity < cutoff_time
        ]
        
        for session_id in expired_sessions:
            self.remove_session(session_id)
            self.logger.info(f"Cleaned up expired session: {session_id}")
    
    def get_session_count(self) -> int:
        """Get the number of active sessions"""
        return len(self.sessions)
    
    async def broadcast_to_all(self, message: dict):
        """Send message to all active sessions"""
        for session in self.sessions.values():
            if session.websocket:
                try:
                    await session.websocket.send_json(message)
                except Exception as e:
                    self.logger.error(f"Error broadcasting to session {session.session_id}: {e}")

# Global session manager instance
session_manager = SessionManager()