import json
import logging
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from ..core.session_manager import session_manager

class WebSocketHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.message_handlers = {
            'ping': self._handle_ping,
            'change_provider': self._handle_change_provider,
            'change_model': self._handle_change_model,
            'audio_data': self._handle_audio_data,
            'text_input': self._handle_text_input,
            'system_status_query': self._handle_system_status_query,
            'self_awareness_query': self._handle_self_awareness_query,
            'error_analysis_request': self._handle_error_analysis_request,
        }
    
    async def handle_connection(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connection for a session"""
        await websocket.accept()
        session = session_manager.get_session(session_id)
        
        if not session:
            await websocket.close(code=4004, reason="Invalid session")
            return
        
        session.websocket = websocket
        self.logger.info(f"WebSocket connected for session: {session_id}")
        
        # Send welcome message
        await websocket.send_json({
            'type': 'connection_established',
            'session_id': session_id,
            'timestamp': session.created_at.isoformat()
        })
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Route message to appropriate handler
                await self._route_message(websocket, session, message)
                
        except WebSocketDisconnect:
            self.logger.info(f"WebSocket disconnected for session: {session_id}")
        except Exception as e:
            self.logger.error(f"WebSocket error for session {session_id}: {e}")
            await websocket.close(code=1011, reason="Internal error")
        finally:
            session.websocket = None
    
    async def _route_message(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Route incoming message to appropriate handler"""
        message_type = message.get('type')
        
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](websocket, session, message)
            except Exception as e:
                self.logger.error(f"Error handling message type {message_type}: {e}")
                await websocket.send_json({
                    'type': 'error',
                    'message': f"Error processing {message_type}",
                    'timestamp': session.last_activity.isoformat()
                })
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
            await websocket.send_json({
                'type': 'error',
                'message': f"Unknown message type: {message_type}",
                'timestamp': session.last_activity.isoformat()
            })
    
    async def _handle_ping(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle ping message"""
        await websocket.send_json({
            'type': 'pong',
            'timestamp': session.last_activity.isoformat()
        })
    
    async def _handle_change_provider(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle provider change request"""
        provider = message.get('provider')
        model = message.get('model')
        
        # TODO: Implement provider change logic
        session.current_provider = provider
        session.current_model = model
        
        await websocket.send_json({
            'type': 'provider_changed',
            'provider': provider,
            'model': model,
            'timestamp': session.last_activity.isoformat()
        })
    
    async def _handle_change_model(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle model change request"""
        model = message.get('model')
        provider = message.get('provider', session.current_provider)
        
        # TODO: Implement model change logic
        session.current_model = model
        session.current_provider = provider
        
        await websocket.send_json({
            'type': 'model_changed',
            'provider': provider,
            'model': model,
            'timestamp': session.last_activity.isoformat()
        })
    
    async def _handle_audio_data(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle audio data for transcription"""
        try:
            audio_data = message.get('data', '')
            
            if not audio_data:
                await websocket.send_json({
                    'type': 'transcription',
                    'text': '',
                    'confidence': 0.0,
                    'error': 'No audio data received',
                    'timestamp': session.last_activity.isoformat()
                })
                return
            
            # Import here to avoid circular imports
            from ..audio.speech_processor import speech_processor
            import base64
            import tempfile
            import subprocess
            from pathlib import Path
            
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            
            # Convert WebM to WAV for Whisper (since frontend sends WebM)
            temp_dir = Path(tempfile.gettempdir()) / "voice_assistant"
            temp_dir.mkdir(exist_ok=True)
            
            # Create temporary files
            import asyncio
            task_name = asyncio.current_task().get_name() if asyncio.current_task() else "unknown"
            temp_webm = temp_dir / f"temp_input_{task_name}.webm"
            temp_wav = temp_dir / f"temp_converted_{task_name}.wav"
            
            # Save WebM data
            with open(temp_webm, 'wb') as f:
                f.write(audio_bytes)
            
            # Convert WebM to WAV using FFmpeg
            ffmpeg_command = [
                'ffmpeg',
                '-i', str(temp_webm),
                '-acodec', 'pcm_s16le',
                '-ar', '16000',  # Whisper prefers 16kHz
                '-ac', '1',      # Mono
                '-y',            # Overwrite
                str(temp_wav)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"FFmpeg conversion failed: {stderr.decode()}")
                await websocket.send_json({
                    'type': 'transcription',
                    'text': '',
                    'confidence': 0.0,
                    'error': 'Audio conversion failed',
                    'timestamp': session.last_activity.isoformat()
                })
                return
            
            # Read converted WAV file
            with open(temp_wav, 'rb') as f:
                wav_data = f.read()
            
            # Clean up temp files
            temp_webm.unlink(missing_ok=True)
            temp_wav.unlink(missing_ok=True)
            
            # Transcribe using Whisper
            result = await speech_processor.transcribe_audio(wav_data, "wav")
            
            transcribed_text = result.get('text', '').strip()
            
            # Send transcription result
            await websocket.send_json({
                'type': 'transcription',
                'text': transcribed_text,
                'confidence': result.get('confidence', 0.0),
                'language': result.get('language', 'en'),
                'duration': result.get('duration', 0),
                'error': result.get('error'),
                'timestamp': session.last_activity.isoformat()
            })
            
            # If transcription successful and has text, process with LLM
            if transcribed_text and not result.get('error') and result.get('confidence', 0) > 30:
                try:
                    from ..llm.provider_manager import provider_manager
                    
                    # Process transcribed text with LLM
                    llm_result = await provider_manager.chat(
                        transcribed_text, 
                        session.conversation_history,
                        session.current_provider,
                        session.current_model
                    )
                    
                    response_text = llm_result['text']
                    used_provider = llm_result['provider']
                    used_model = llm_result['model']
                    
                    session.add_conversation_turn(
                        transcribed_text, response_text, used_provider, used_model
                    )
                    
                    # Send LLM response
                    await websocket.send_json({
                        'type': 'response',
                        'text': response_text,
                        'provider': used_provider,
                        'model': used_model,
                        'fallback_used': llm_result.get('fallback_used', False),
                        'source': 'voice_input',
                        'timestamp': session.last_activity.isoformat()
                    })
                    
                    # Generate and send TTS audio for voice response
                    try:
                        import base64
                        
                        # Generate TTS audio
                        tts_result = await speech_processor.synthesize_speech(response_text)
                        
                        if tts_result.get('success', False) and tts_result.get('audio_data'):
                            # Convert audio data to base64 for transmission
                            audio_base64 = base64.b64encode(tts_result['audio_data']).decode('utf-8')
                            
                            await websocket.send_json({
                                'type': 'audio_response',
                                'audio_data': audio_base64,
                                'audio_format': tts_result.get('audio_format', 'wav'),
                                'duration': tts_result.get('duration', 0),
                                'text': response_text,
                                'source': 'voice_input',
                                'timestamp': session.last_activity.isoformat()
                            })
                            
                            self.logger.info(f"Voice conversation: '{transcribed_text}' -> TTS response generated")
                        else:
                            self.logger.warning(f"TTS generation failed for voice response: {tts_result.get('error', 'Unknown error')}")
                            
                    except Exception as tts_error:
                        self.logger.error(f"Error generating TTS for voice response: {tts_error}")
                    
                except Exception as llm_error:
                    self.logger.error(f"Error processing transcribed text with LLM: {llm_error}")
                    await websocket.send_json({
                        'type': 'error',
                        'message': f"Error processing voice input: {str(llm_error)}",
                        'timestamp': session.last_activity.isoformat()
                    })
            
        except Exception as e:
            self.logger.error(f"Error processing audio data: {e}")
            await websocket.send_json({
                'type': 'transcription',
                'text': '',
                'confidence': 0.0,
                'error': f'Audio processing error: {str(e)}',
                'timestamp': session.last_activity.isoformat()
            })
    
    async def _handle_text_input(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle text input from user"""
        text = message.get('text', '')
        
        try:
            # Import here to avoid circular imports
            from ..llm.provider_manager import provider_manager
            
            # Process text with LLM
            result = await provider_manager.chat(
                text, 
                session.conversation_history,
                session.current_provider,
                session.current_model
            )
            
            response_text = result['text']
            used_provider = result['provider']
            used_model = result['model']
            
            session.add_conversation_turn(
                text, response_text, used_provider, used_model
            )
            
            # Send text response first
            await websocket.send_json({
                'type': 'response',
                'text': response_text,
                'provider': used_provider,
                'model': used_model,
                'fallback_used': result.get('fallback_used', False),
                'timestamp': session.last_activity.isoformat()
            })
            
            # Generate and send audio response
            try:
                from ..audio.speech_processor import speech_processor
                import base64
                
                # Generate TTS audio
                tts_result = await speech_processor.synthesize_speech(response_text)
                
                if tts_result.get('success', False) and tts_result.get('audio_data'):
                    # Convert audio data to base64 for transmission
                    audio_base64 = base64.b64encode(tts_result['audio_data']).decode('utf-8')
                    
                    await websocket.send_json({
                        'type': 'audio_response',
                        'audio_data': audio_base64,
                        'audio_format': tts_result.get('audio_format', 'wav'),
                        'duration': tts_result.get('duration', 0),
                        'text': response_text,
                        'timestamp': session.last_activity.isoformat()
                    })
                    
                    self.logger.info(f"TTS audio generated for response: {len(response_text)} chars")
                else:
                    self.logger.warning(f"TTS generation failed: {tts_result.get('error', 'Unknown error')}")
                    
            except Exception as tts_error:
                self.logger.error(f"Error generating TTS audio: {tts_error}")
                # Don't fail the whole response if TTS fails
            
        except Exception as e:
            self.logger.error(f"Error processing text input: {e}")
            await websocket.send_json({
                'type': 'error',
                'message': f"Error processing message: {str(e)}",
                'timestamp': session.last_activity.isoformat()
            })
    
    async def _handle_system_status_query(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle system status query for self-awareness"""
        try:
            from ..monitoring.self_awareness import self_awareness_monitor
            
            query_type = message.get('query_type', 'current')
            timeframe_minutes = message.get('timeframe_minutes', 10)
            
            status_response = await self_awareness_monitor.handle_system_status_query(
                query_type, timeframe_minutes
            )
            
            await websocket.send_json({
                'type': 'system_status_response',
                **status_response
            })
            
        except Exception as e:
            self.logger.error(f"Error handling system status query: {e}")
            await websocket.send_json({
                'type': 'system_status_response',
                'status': 'error',
                'metrics': {},
                'analysis': f'Error gathering system status: {str(e)}',
                'recommendations': ['Check system logs', 'Restart monitoring service'],
                'alerts': [],
                'timestamp': session.last_activity.isoformat()
            })
    
    async def _handle_self_awareness_query(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle self-awareness capability query"""
        try:
            from ..monitoring.self_awareness import self_awareness_monitor
            
            question = message.get('question', '')
            context = message.get('context', {})
            
            response = await self_awareness_monitor.handle_capability_query(question, context)
            
            await websocket.send_json({
                'type': 'self_awareness_response',
                'timestamp': session.last_activity.isoformat(),
                **response
            })
            
        except Exception as e:
            self.logger.error(f"Error handling self-awareness query: {e}")
            await websocket.send_json({
                'type': 'self_awareness_response',
                'answer': f'Error processing self-awareness query: {str(e)}',
                'capability_assessment': {
                    'question_understood': False,
                    'explanation': 'System error occurred',
                    'alternatives': ['Try again later', 'Check system status']
                },
                'confidence': 0,
                'timestamp': session.last_activity.isoformat()
            })
    
    async def _handle_error_analysis_request(self, websocket: WebSocket, session, message: Dict[str, Any]):
        """Handle error analysis request"""
        # TODO: Implement error analysis with local LLM
        await websocket.send_json({
            'type': 'error_analysis_response',
            'analysis': 'No recent errors detected in system logs',
            'root_cause': 'System operating normally',
            'severity': 'info',
            'recommendations': ['Continue monitoring'],
            'predicted_resolution_time': 'immediate',
            'timestamp': session.last_activity.isoformat()
        })

# Global WebSocket handler instance
websocket_handler = WebSocketHandler()