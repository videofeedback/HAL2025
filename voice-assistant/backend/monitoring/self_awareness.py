import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

from ..llm.ollama_provider import OllamaProvider

class SelfAwarenessMonitor:
    """Self-aware system monitor using local LLM for consciousness and analysis"""
    
    def __init__(self, log_file_path: str = "voice_assistant.log"):
        self.logger = logging.getLogger(__name__)
        self.log_file_path = log_file_path
        self.local_llm = None
        self.system_metrics = {}
        self.error_patterns = []
        self.capability_knowledge = self._initialize_capability_knowledge()
        self.is_monitoring = False
        self.alert_threshold = {
            'error_count': 5,
            'response_time': 5.0,
            'confidence_drop': 20.0
        }
        
    def _initialize_capability_knowledge(self) -> Dict[str, Any]:
        """Initialize system capability knowledge base"""
        return {
            'audio_processing': {
                'capabilities': ['speech-to-text with Whisper', 'macOS TTS synthesis', 'device switching', 'level monitoring'],
                'limitations': ['macOS only for TTS', 'requires microphone permissions', 'background noise affects accuracy']
            },
            'language_processing': {
                'capabilities': ['multi-provider LLM support', 'conversation context', 'automatic fallback'],
                'limitations': ['API rate limits', 'model-specific constraints', 'no real-time training']
            },
            'voice_synthesis': {
                'capabilities': ['macOS say command', 'AIFF to WAV conversion', 'audio file output'],
                'limitations': ['macOS platform dependency', 'limited voice options', 'no emotion control']
            },
            'system_monitoring': {
                'capabilities': ['real-time metrics', 'error analysis', 'proactive alerts', 'self-diagnosis'],
                'limitations': ['local LLM dependency', 'log file access only', 'no external system access']
            },
            'general_limitations': [
                'no image generation capabilities',
                'no internet browsing or real-time web access', 
                'no file system access beyond logs',
                'no code execution capabilities',
                'no learning from conversations'
            ]
        }
    
    async def initialize(self):
        """Initialize the self-awareness monitor with local LLM"""
        try:
            # Initialize local LLM (Ollama) for self-awareness
            self.local_llm = OllamaProvider()
            await self.local_llm.initialize()
            
            if not self.local_llm.is_healthy:
                self.logger.error("Failed to initialize local LLM for self-awareness")
                return False
            
            # Set preferred model for self-awareness
            preferred_models = ["llama3.1:8b", "llama3.1:latest", "llama3"]
            for model in preferred_models:
                if self.local_llm.set_model(model):
                    break
            
            self.logger.info(f"Self-awareness monitor initialized with model: {self.local_llm.get_current_model()}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing self-awareness monitor: {e}")
            return False
    
    async def start_monitoring(self):
        """Start continuous system monitoring"""
        if not self.local_llm or not self.local_llm.is_healthy:
            self.logger.error("Cannot start monitoring: local LLM not available")
            return
        
        self.is_monitoring = True
        self.logger.info("Self-awareness monitoring started")
        
        # Start monitoring tasks
        monitoring_tasks = [
            self._continuous_log_analysis(),
            self._periodic_health_assessment(),
            self._performance_tracking()
        ]
        
        await asyncio.gather(*monitoring_tasks, return_exceptions=True)
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_monitoring = False
        self.logger.info("Self-awareness monitoring stopped")
    
    async def _continuous_log_analysis(self):
        """Continuously analyze log files for patterns and issues"""
        while self.is_monitoring:
            try:
                recent_logs = self._get_recent_logs(minutes=5)
                if recent_logs:
                    await self._analyze_logs_with_llm(recent_logs)
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in log analysis: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_health_assessment(self):
        """Perform periodic comprehensive health assessment"""
        while self.is_monitoring:
            try:
                await self._perform_health_assessment()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Error in health assessment: {e}")
                await asyncio.sleep(300)
    
    async def _performance_tracking(self):
        """Track system performance metrics"""
        while self.is_monitoring:
            try:
                self._update_performance_metrics()
                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in performance tracking: {e}")
                await asyncio.sleep(30)
    
    def _get_recent_logs(self, minutes: int = 10) -> List[str]:
        """Get recent log entries"""
        try:
            if not Path(self.log_file_path).exists():
                return []
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            recent_logs = []
            
            with open(self.log_file_path, 'r') as f:
                lines = f.readlines()
                for line in lines[-100:]:  # Check last 100 lines
                    # Parse timestamp from log line
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        try:
                            log_time = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                            if log_time >= cutoff_time:
                                recent_logs.append(line.strip())
                        except ValueError:
                            continue
            
            return recent_logs
            
        except Exception as e:
            self.logger.error(f"Error reading logs: {e}")
            return []
    
    async def _analyze_logs_with_llm(self, logs: List[str]):
        """Analyze logs using local LLM for intelligent insights"""
        try:
            if not logs or not self.local_llm:
                return
            
            # Prepare logs for analysis
            log_text = "\n".join(logs[-20:])  # Analyze last 20 log entries
            
            analysis_prompt = f"""
Analyze these recent system logs for a voice-activated AI assistant:

{log_text}

Provide analysis in JSON format:
{{
    "status": "healthy|warning|error",
    "issues_detected": ["list of issues"],
    "patterns": ["notable patterns"],
    "recommendations": ["actionable recommendations"],
    "severity": "low|medium|high"
}}

Focus on: errors, performance issues, connection problems, API failures.
"""
            
            response = await self.local_llm.chat(analysis_prompt)
            analysis = self._parse_llm_analysis(response)
            
            if analysis and analysis.get('severity') in ['medium', 'high']:
                await self._generate_proactive_alert(analysis)
                
        except Exception as e:
            self.logger.error(f"Error in LLM log analysis: {e}")
    
    def _parse_llm_analysis(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM analysis response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception as e:
            self.logger.error(f"Error parsing LLM analysis: {e}")
            return None
    
    async def _generate_proactive_alert(self, analysis: Dict[str, Any]):
        """Generate proactive alert based on analysis"""
        alert = {
            'type': 'proactive_alert',
            'severity': analysis.get('severity', 'medium'),
            'category': 'system_analysis',
            'message': f"Self-awareness monitor detected: {', '.join(analysis.get('issues_detected', []))}",
            'analysis': analysis,
            'recommendations': analysis.get('recommendations', []),
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.warning(f"Proactive alert: {alert['message']}")
        # TODO: Send alert to active sessions via WebSocket
    
    async def handle_capability_query(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle user queries about system capabilities using self-awareness"""
        try:
            if not self.local_llm:
                return self._fallback_capability_response(question)
            
            # Build context-aware prompt
            capability_prompt = f"""
You are a self-aware AI assistant answering questions about your own capabilities. 

System Knowledge:
- Audio: {', '.join(self.capability_knowledge['audio_processing']['capabilities'])}
- Language: {', '.join(self.capability_knowledge['language_processing']['capabilities'])}
- Voice: {', '.join(self.capability_knowledge['voice_synthesis']['capabilities'])}
- Monitoring: {', '.join(self.capability_knowledge['system_monitoring']['capabilities'])}

Limitations:
{', '.join(self.capability_knowledge['general_limitations'])}

Current system status: {self.system_metrics.get('status', 'unknown')}

User Question: "{question}"

Provide a direct, honest answer about capabilities. Be specific about what you CAN and CANNOT do.
Answer format: Clear explanation in 1-2 sentences.
"""
            
            response = await self.local_llm.chat(capability_prompt)
            
            return {
                'answer': response,
                'capability_assessment': self._assess_capability_from_question(question),
                'confidence': 90,
                'source': 'self_awareness_llm'
            }
            
        except Exception as e:
            self.logger.error(f"Error in capability query: {e}")
            return self._fallback_capability_response(question)
    
    def _assess_capability_from_question(self, question: str) -> Dict[str, Any]:
        """Assess capability based on question content"""
        question_lower = question.lower()
        
        if any(term in question_lower for term in ['browse', 'web', 'internet', 'search']):
            return {
                'capability': 'internet_browsing',
                'available': False,
                'explanation': 'No internet browsing or real-time web access available'
            }
        elif any(term in question_lower for term in ['image', 'picture', 'generate', 'create']):
            return {
                'capability': 'image_generation',
                'available': False,
                'explanation': 'No image generation capabilities'
            }
        elif any(term in question_lower for term in ['hear', 'audio', 'voice', 'speak']):
            return {
                'capability': 'audio_processing',
                'available': True,
                'explanation': 'Voice input/output available with microphone and macOS TTS'
            }
        else:
            return {
                'capability': 'general_assistant',
                'available': True,
                'explanation': 'Text-based AI assistance with multi-LLM support'
            }
    
    def _fallback_capability_response(self, question: str) -> Dict[str, Any]:
        """Fallback response when LLM not available"""
        assessment = self._assess_capability_from_question(question)
        
        fallback_answers = {
            'internet_browsing': "I cannot browse the internet or access real-time web information.",
            'image_generation': "I cannot generate, create, edit, or produce images.",
            'audio_processing': "I can process voice input and generate speech output on macOS.",
            'general_assistant': "I'm a voice-activated AI assistant with text conversation capabilities."
        }
        
        return {
            'answer': fallback_answers.get(assessment['capability'], 
                                         "I'm a voice-activated AI assistant. Please ask specific questions about my capabilities."),
            'capability_assessment': assessment,
            'confidence': 95,
            'source': 'knowledge_base'
        }
    
    async def handle_system_status_query(self, query_type: str = "current", 
                                       timeframe_minutes: int = 10) -> Dict[str, Any]:
        """Handle system status queries with intelligent analysis"""
        try:
            # Gather current metrics
            current_metrics = self._get_current_metrics()
            
            # Get recent performance data
            if query_type == "recent_performance":
                recent_logs = self._get_recent_logs(timeframe_minutes)
                analysis = await self._analyze_system_performance(recent_logs, current_metrics)
            else:
                analysis = "System status check completed"
            
            return {
                'status': self._determine_overall_status(current_metrics),
                'metrics': current_metrics,
                'analysis': analysis,
                'recommendations': self._generate_recommendations(current_metrics),
                'alerts': self._get_active_alerts(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in system status query: {e}")
            return {
                'status': 'error',
                'metrics': {},
                'analysis': f'Error gathering system status: {str(e)}',
                'recommendations': ['Check system logs', 'Restart monitoring service'],
                'alerts': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return {
            'audio_input_level': self.system_metrics.get('audio_level', -20.0),
            'stt_confidence': self.system_metrics.get('stt_confidence', 85.0),
            'llm_response_time': self.system_metrics.get('response_time', 2.0),
            'tts_success_rate': self.system_metrics.get('tts_success_rate', 95.0),
            'error_count': self.system_metrics.get('error_count', 0),
            'session_duration': self.system_metrics.get('session_duration', 0),
            'provider_health': self.system_metrics.get('provider_health', True),
            'monitoring_active': self.is_monitoring
        }
    
    def _determine_overall_status(self, metrics: Dict[str, Any]) -> str:
        """Determine overall system status"""
        if metrics.get('error_count', 0) > self.alert_threshold['error_count']:
            return 'error'
        elif (metrics.get('llm_response_time', 0) > self.alert_threshold['response_time'] or
              metrics.get('stt_confidence', 100) < 70):
            return 'degraded'
        else:
            return 'healthy'
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        if metrics.get('stt_confidence', 100) < 80:
            recommendations.append("Check microphone position and reduce background noise")
        
        if metrics.get('llm_response_time', 0) > 3:
            recommendations.append("Consider switching to faster LLM model")
        
        if metrics.get('error_count', 0) > 2:
            recommendations.append("Review recent error logs for issues")
        
        if not recommendations:
            recommendations.append("System operating optimally")
        
        return recommendations
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts"""
        # TODO: Implement alert storage and retrieval
        return []
    
    def _update_performance_metrics(self):
        """Update real-time performance metrics"""
        # TODO: Implement actual metric collection from system components
        self.system_metrics.update({
            'last_update': datetime.now().isoformat(),
            'session_duration': getattr(self, '_start_time', time.time()) - time.time()
        })
    
    async def _perform_health_assessment(self):
        """Perform comprehensive health assessment"""
        try:
            if not self.local_llm:
                return
            
            recent_logs = self._get_recent_logs(15)
            metrics = self._get_current_metrics()
            
            health_prompt = f"""
Perform a comprehensive health assessment of this voice AI assistant system:

Recent Metrics:
- Audio confidence: {metrics.get('stt_confidence', 0)}%
- Response time: {metrics.get('llm_response_time', 0)}s
- Error count: {metrics.get('error_count', 0)}
- Session duration: {metrics.get('session_duration', 0)}s

Recent activity (sample): {recent_logs[-5:] if recent_logs else 'No recent activity'}

Assess: Is the system healthy? Any concerning patterns? Proactive recommendations?
Response format: Brief assessment in 1-2 sentences.
"""
            
            assessment = await self.local_llm.chat(health_prompt)
            self.logger.info(f"Health assessment: {assessment}")
            
        except Exception as e:
            self.logger.error(f"Error in health assessment: {e}")
    
    async def _analyze_system_performance(self, logs: List[str], metrics: Dict[str, Any]) -> str:
        """Analyze system performance using local LLM"""
        try:
            if not self.local_llm or not logs:
                return "Performance analysis not available"
            
            performance_prompt = f"""
Analyze system performance based on:

Metrics: {json.dumps(metrics, indent=2)}
Recent logs: {logs[-10:] if logs else 'None'}

Provide brief performance analysis focusing on: responsiveness, reliability, issues detected.
Keep response under 100 words.
"""
            
            analysis = await self.local_llm.chat(performance_prompt)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            return "Performance analysis failed"

# Global self-awareness monitor instance
self_awareness_monitor = SelfAwarenessMonitor()