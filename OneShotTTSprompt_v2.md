# OneShotTTSprompt v2.0 - Modular Voice-Activated AI Assistant

**Complete specification for building a Self-Aware Voice-to-Text AI Assistant with Multi-LLM Provider Support**
FOCUS ON THE SELF-AWARENESS SECTION OF THIS FILE.
READ THE FULL FILE TO HAVE A 10,000 FEET VIEW AND THEN PROCEEDE FROM THE BEGINNING, KEEPING IN MIND ALL THIS DOCUMENT.
---

## 🎯 **PROJECT OVERVIEW**

Build a production-ready voice-activated AI assistant with:
- **Multi-LLM Provider Support** (OpenAI, Claude, XAI, LM Studio, Ollama)
- **Self-Awareness Monitor** using dedicated local LLM for error handling
- **Real-time Voice Processing** (Speech-to-Text, Text-to-Speech)
- **Intelligent System Monitoring** with proactive error handling
- **Modular Architecture** for independent development and testing

---

## 🏗️ **CORE ARCHITECTURE**

### System Requirements
- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: Vanilla JavaScript (ES6+)
- **Audio Processing**: OpenAI Whisper + macOS TTS
- **Local LLM**: Ollama (llama3.1:8b-instruct)
- **Communication**: WebSocket real-time bidirectional
- **Platform**: macOS (TTS dependency)

### Project Structure
```
voice-assistant/
├── backend/
│   ├── core/                    # Core system components
│   ├── audio/                   # Audio processing modules
│   ├── llm/                     # LLM provider system
│   ├── monitoring/              # Self-awareness monitor
│   └── api/                     # FastAPI routes and WebSocket
├── frontend/
│   ├── components/              # UI components
│   ├── services/                # WebSocket and API clients
│   └── assets/                  # Static files
├── config/
│   ├── keys/                    # API key files (gitignored)
│   └── settings/                # Configuration files
└── docs/                        # Documentation and guides
```

---

## 📋 **ENVIRONMENT SETUP**

### Prerequisites Checklist
- [ ] **Python 3.9+** installed
- [ ] **FFmpeg** installed (`brew install ffmpeg`)
- [ ] **Ollama** installed (`brew install ollama`)
- [ ] **Node.js 16+** (for development tools)
- [ ] **macOS** (for TTS functionality)

### API Keys Required
```bash
# Create these files in config/keys/
config/keys/OpenAI.key          # OpenAI API key (sk-proj-...)
config/keys/Claude.key          # Anthropic API key (sk-ant-...)
config/keys/XAI.key             # XAI API key (optional)
```

### Local Services Setup
```bash
# Start Ollama service
ollama serve

# Pull required model for self-awareness
ollama pull llama3.1:8b-instruct

# Optional: Start LM Studio on localhost:1234
# Download and run LM Studio application
```

### Python Dependencies
```bash
# Install core dependencies
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install websockets==12.0
pip install openai-whisper==20231117
pip install openai==1.3.0
pip install anthropic==0.8.0
pip install aiohttp==3.9.0
pip install torch torchaudio
```

---

## 🧩 **MODULE SPECIFICATIONS**

## Module 1: Core System Foundation

### Purpose
FastAPI server with WebSocket communication and session management

### Key Components
- **WebSocket Server**: Real-time bidirectional communication
- **Session Manager**: Handle user sessions and cleanup
- **Configuration Manager**: Load settings and API keys
- **Health Check System**: Monitor service availability

### Implementation Requirements
- FastAPI application with WebSocket endpoints
- Session UUID tracking and lifecycle management
- Graceful connection handling and reconnection logic
- Environment-based configuration loading

### Validation Criteria
- [ ] WebSocket connects and maintains stable connection
- [ ] Session creates and cleans up properly
- [ ] Health check endpoint responds correctly
- [ ] Configuration loads without errors

---

## Module 2: Audio Processing Pipeline

### Purpose
Handle speech-to-text, text-to-speech, and audio device management

### Key Components
- **Speech-to-Text**: OpenAI Whisper integration
- **Text-to-Speech**: macOS `say` command with audio conversion
- **Audio Device Manager**: Microphone selection and monitoring
- **VU Meter**: Real-time audio level visualization

### Implementation Requirements
- Whisper model loading and audio transcription
- macOS TTS with AIFF to WAV conversion using FFmpeg
- Web Audio API integration for device management
- Real-time audio level monitoring and visualization

### Validation Criteria
- [ ] Audio input detects and processes speech
- [ ] Transcription returns with confidence scores
- [ ] TTS generates clear audio output files
- [ ] Audio devices can be switched dynamically
- [ ] VU meter shows accurate audio levels

---

## Module 3: Multi-LLM Provider System

### Purpose
Unified interface for multiple LLM providers with automatic fallback

### Key Components
- **Provider Manager**: Centralized provider coordination
- **Base Provider**: Abstract interface for all providers
- **Individual Providers**: OpenAI, Claude, XAI, LM Studio, Ollama
- **Fallback Chain**: Automatic provider switching on failure

### Implementation Requirements
- Abstract base class with consistent interface
- Provider-specific implementations with error handling
- Health checking and automatic failover logic
- Model selection and parameter management

### Provider Specifications
```python
# Base Provider Interface
class BaseLLMProvider:
    async def chat(self, message: str, history: list, model: str = None) -> str
    async def health_check(self, model: str = None) -> bool
    def get_available_models(self) -> list
    def set_model(self, model: str) -> bool
```

### Validation Criteria
- [ ] All providers connect and respond correctly
- [ ] Fallback chain activates on provider failure
- [ ] Model switching works for each provider
- [ ] Health checks accurately report status
- [ ] API key management secure and functional

---

## Module 4: Self-Awareness Monitor

### Purpose
Dedicated local LLM for system consciousness and intelligent monitoring

### Key Components
- **Self-Aware Monitor**: Main consciousness engine
- **Log Analyzer**: Real-time log file analysis
- **System Knowledge**: Capability assessment database
- **Error Diagnoser**: LLM-powered error analysis
- **Health Tracker**: Continuous system monitoring

### Core Functionality
- **System Status Analysis**: Real-time performance metrics
- **Intelligent User Responses**: Context-aware capability answers
- **Proactive Alerts**: Predictive issue detection
- **Error Diagnosis**: LLM reasoning for troubleshooting
- **Performance Optimization**: Automatic tuning suggestions

### Self-Awareness Capabilities
```python
# System understands and can explain:
capabilities = {
    'audio_processing': ['speech-to-text', 'device switching', 'level monitoring'],
    'language_processing': ['multi-provider LLM', 'conversation context'],
    'voice_synthesis': ['macOS TTS', 'audio conversion'],
    'limitations': ['no image generation', 'no internet browsing', 'no file access']
}
```

### User Query Handling
- **"Is this working?"** → System metrics and health status
- **"Do you hear me?"** → Audio input analysis and confidence
- **"Can you browse the web?"** → Clear limitation explanation
- **"You seem slow"** → Performance analysis and optimization

### Validation Criteria
- [ ] Local LLM responds to system queries
- [ ] Log analysis identifies patterns and issues
- [ ] User capability questions answered accurately
- [ ] Proactive alerts trigger appropriately
- [ ] Error diagnosis provides useful insights

---

## Module 5: Frontend Interface

### Purpose
User interface for voice interaction and system monitoring

### Key Components
- **Main Interface**: Voice interaction controls
- **Provider Selector**: LLM provider and model selection
- **System Monitor**: Real-time metrics and alerts
- **Audio Controls**: Device selection and level monitoring

### UI Design Approach
**Note: UI styling will be based on provided design image named template.png. Create functional components first, then apply styling from image reference.**

### Core UI Components
```javascript
// Component Structure (styling to be applied from image)
- VoiceInterface: Main interaction area
- TextInterface: Create an USER input text area for alternative to voice input
- ProviderSelector: Dropdown for LLM selection
- SystemMonitor: Collapsible metrics panel
- AudioControls: Device and level management
- AlertsPanel: System notifications and warnings
- DisconnectionButton: Terminates all the instances and web-sockets sessions
```

### Functional Requirements
- Voice recording start/stop controls
- Real-time audio level visualization
- TextInput for the user typing input instead of waiting for voice
- Provider/model selection dropdowns
- System status indicators
- Error/alert notification system
- WebSocket connection status
- DisconnectionButton terminates all the initiated WebSockets and LLMs sessions

### Validation Criteria
- [ ] Voice recording triggers correctly
- [ ] Audio levels display in real-time
- [ ] Text input bypass voice-to-text
- [ ] Provider switching updates backend
- [ ] System metrics refresh automatically
- [ ] Alerts display with appropriate severity
- [ ] All UI controls respond to user interaction

---

## Module 6: Integration & Communication

### Purpose
Connect all modules through WebSocket messaging and shared interfaces

### Key Components
- **Message Protocol**: Standardized WebSocket communication
- **Event System**: Inter-module communication
- **State Management**: Shared application state
- **Error Handling**: Unified error reporting and recovery

### WebSocket Message Types
```javascript
// Core message types for module communication
const MESSAGE_TYPES = {
    // Audio pipeline
    AUDIO_DATA: 'audio_data',
    TRANSCRIPTION_RESULT: 'transcription_result',
    TTS_REQUEST: 'tts_request',
    
    // LLM providers
    CHAT_REQUEST: 'chat_request',
    PROVIDER_SWITCH: 'provider_switch',
    PROVIDER_STATUS: 'provider_status',
    
    // Self-awareness
    SYSTEM_QUERY: 'system_query',
    HEALTH_UPDATE: 'health_update',
    ALERT_NOTIFICATION: 'alert_notification',
    
    // UI events
    UI_STATE_CHANGE: 'ui_state_change',
    USER_ACTION: 'user_action'
};
```

### Validation Criteria
- [ ] All modules communicate through WebSocket
- [ ] Message routing works correctly
- [ ] Error states propagate appropriately
- [ ] System state remains consistent
- [ ] Module failures don't crash entire system

---

## 🚀 **IMPLEMENTATION PHASES**

### Phase 1: Foundation 
1. **Core System Setup**
   - FastAPI server with WebSocket
   - Basic session management
   - Configuration loading
   - Health check endpoints

2. **Environment Validation**
   - API key verification
   - Local service connectivity
   - Dependency installation verification

### Phase 2: Audio Pipeline 
1. **Audio Input Processing**
   - Whisper integration
   - Device management
   - Real-time transcription

2. **Audio Output Generation**
   - macOS TTS integration
   - Audio format conversion
   - Output quality validation

### Phase 3: LLM Integration 
1. **Provider System**
   - Base provider architecture
   - Individual provider implementations
   - Health checking and failover

2. **Model Management**
   - Model selection interface
   - Performance optimization
   - Error handling and recovery

### Phase 4: Self-Awareness
1. **Monitor Setup**
   - Local LLM integration
   - Log analysis system
   - System knowledge base

2. **Intelligence Layer**
   - User query handling
   - Proactive monitoring
   - Error diagnosis

### Phase 5: Frontend Interface
1. **UI Components**
   - Create functional components
   - WebSocket integration
   - Real-time updates

2. **Design Application**
   - Apply styling from provided image
   - Responsive behavior
   - User experience refinement

### Phase 6: Integration & Testing
1. **End-to-End Integration**
   - Module connectivity testing
   - Performance optimization
   - Error handling validation

2. **Production Preparation**
   - Security hardening
   - Performance tuning
   - Deployment procedures

---

## ✅ **VALIDATION STRATEGY**

### Module Testing
Each module must pass independent validation before integration:

```bash
# Core system validation
curl -X GET http://localhost:8000/health
# Should return: {"status": "healthy", "timestamp": "..."}

# Audio pipeline validation
# Record 5-second audio sample
# Verify transcription confidence > 80%
# Verify TTS output file size > 100KB

# LLM provider validation
# Test each provider with simple query
# Verify fallback chain activates
# Confirm model switching works

# Self-awareness validation
# Query: "Is this working?"
# Verify detailed system metrics returned
# Test capability assessment accuracy

# Frontend validation
# All UI controls functional
# WebSocket maintains connection
# Real-time updates working
```

### Integration Testing
```bash
# End-to-end workflow validation
1. Start voice recording
2. Speak test phrase
3. Verify transcription accuracy
4. Confirm LLM response generation
5. Validate TTS audio output
6. Check system monitoring throughout
```

### Performance Benchmarks
- **Transcription Time**: < 2 seconds for 10-second audio
- **LLM Response Time**: < 3 seconds for simple queries
- **TTS Generation**: < 1 second for 20-word responses
- **System Monitoring**: Updates every 30 seconds
- **Memory Usage**: < 2GB total system footprint

---

## 🛠️ **TROUBLESHOOTING GUIDE**

### Common Setup Issues

**Ollama Connection Failed**
```bash
# Check if Ollama is running
ollama list
# If not running: ollama serve
# Pull model: ollama pull llama3.1:8b-instruct
```

**API Key Authentication Errors**
```bash
# Verify key file format
cat config/keys/OpenAI.key
# Should start with: sk-proj- or sk-
# Check file permissions: chmod 600 config/keys/*.key
```

**Audio Processing Issues**
```bash
# Check FFmpeg installation
ffmpeg -version
# Verify microphone permissions in macOS System Preferences
# Test TTS: say "Hello, this is a test"
```

**WebSocket Connection Problems**
```bash
# Check port availability
lsof -i :8000
# Verify CORS settings in FastAPI
# Check browser console for connection errors
```

### Performance Optimization

**Slow Response Times**
- Switch to faster LLM models (gpt-3.5-turbo, claude-haiku)
- Reduce conversation history length
- Enable model caching where possible

**High Memory Usage**
- Use smaller local models (phi3:mini instead of llama3.1:70b)
- Implement conversation history pruning
- Optimize audio buffer sizes

**Audio Quality Issues**
- Adjust microphone input levels
- Reduce background noise
- Switch audio input devices

---

## 🎨 **UI DESIGN INTEGRATION**

**Design Process:**
1. **Build Functional Components First** - Create all UI components with basic styling
2. **Apply Design from Image** - Use provided UI image as styling reference
3. **Maintain Responsive Behavior** - Ensure components work on different screen sizes
4. **Preserve Functionality** - Keep all interactive elements working during restyling

**Component Flexibility:**
- All components built with CSS classes for easy restyling
- No hard-coded dimensions or measurements
- Modular CSS structure for independent component styling
- Design tokens for consistent theming


**Self-Aware ASSISTANT Flexibilit:**
Incorporate this instructions to the LLM agent:
  This Self-Aware AI Assistant implementation creates a truly intelligent voice-to-text system that understands itself deeply, can monitor its own performance, diagnose issues, and communicate its capabilities and limitations clearly to users. The dedicated Local LLM monitor provides continuous system consciousness that enhances the overall user experience through proactive assistance and intelligent error handling.

**Styling Approach:**
```css
/* Component-based styling ready for design application */
.voice-interface { /* Styling from image */ }
.provider-selector { /* Styling from image */ }
.system-monitor { /* Styling from image */ }
.audio-controls { /* Styling from image */ }
```

---

## 📝 **DEPLOYMENT CHECKLIST**

### Pre-Deployment Validation
- [ ] All API keys configured and tested
- [ ] Local services (Ollama) running and accessible
- [ ] All modules pass individual validation tests
- [ ] End-to-end workflow completes successfully
- [ ] Performance benchmarks met
- [ ] Error handling tested and working
- [ ] Security configurations applied
- [ ] Backup and recovery procedures documented

### Production Readiness
- [ ] Environment variables properly configured
- [ ] Logging levels set appropriately
- [ ] Monitor dashboards configured
- [ ] Error alerting systems active
- [ ] User documentation complete
- [ ] Support procedures documented

---

## 🔄 **MAINTENANCE & UPDATES**

### Regular Maintenance Tasks
- **Weekly**: Check API key validity and usage limits
- **Monthly**: Update LLM models and providers
- **Quarterly**: Performance optimization review
- **As Needed**: Security patches and dependency updates

### Monitoring & Alerts
- System health checks every 5 minutes
- API provider status monitoring
- Performance threshold alerts
- Error rate monitoring
- User satisfaction metrics



### SELF-AWARENESS EXAMPLE IMPLEMENTATION ###

### Enhanced WebSocket Message Protocol with Self-Awareness Support
```javascript
// WebSocket message types for provider, model, and self-awareness management
const WEBSOCKET_MESSAGES = {
    // Provider and model management
    CHANGE_PROVIDER: 'change_provider',
    CHANGE_MODEL: 'change_model',
    PROVIDER_CHANGED: 'provider_changed', 
    MODEL_CHANGED: 'model_changed',
    PROVIDER_STATUS: 'provider_status',
    MODEL_STATUS: 'model_status',
    PROVIDER_ERROR: 'provider_error',
    MODEL_ERROR: 'model_error',
    
    // Self-Awareness Monitor messages
    SYSTEM_STATUS_QUERY: 'system_status_query',
    SYSTEM_STATUS_RESPONSE: 'system_status_response',
    SELF_AWARENESS_QUERY: 'self_awareness_query',
    SELF_AWARENESS_RESPONSE: 'self_awareness_response',
    ERROR_ANALYSIS_REQUEST: 'error_analysis_request',
    ERROR_ANALYSIS_RESPONSE: 'error_analysis_response',
    PROACTIVE_ALERT: 'proactive_alert',
    CAPABILITY_QUERY: 'capability_query',
    CAPABILITY_RESPONSE: 'capability_response',
    HEALTH_CHECK_UPDATE: 'health_check_update',
    
    // Existing messages
    AUDIO: 'audio',
    TRANSCRIPTION: 'transcription',
    RESPONSE: 'response',
    AUDIO_RESPONSE: 'audio_response'
};

// Enhanced provider change message
{
    "type": "change_provider",
    "provider": "claude",
    "model": "claude-3-5-sonnet-20241022",
    "timestamp": "2024-01-20T10:30:00Z"
}

// Model change message
{
    "type": "change_model",
    "provider": "openai",
    "model": "o3-mini",
    "previous_model": "gpt-4o",
    "timestamp": "2024-01-20T10:30:00Z"
}

// Enhanced provider status with model information
{
    "type": "provider_status",
    "providers": {
        "openai": {
            "available": true,
            "current_model": "gpt-4o",
            "model_health": true,
            "models": [
                {"id": "o3-mini", "name": "o3-mini", "available": true},
                {"id": "gpt-4o", "name": "GPT-4o", "available": true},
                {"id": "gpt-4", "name": "GPT-4", "available": false}
            ]
        },
        "claude": {
            "available": true,
            "current_model": "claude-3-5-sonnet-20241022",
            "model_health": true,
            "models": [...]
        }
    }
}

// Self-Awareness System Status Query
{
    "type": "system_status_query",
    "query_type": "recent_performance",
    "timeframe_minutes": 10,
    "include_logs": true,
    "include_predictions": true,
    "timestamp": "2024-01-20T10:30:00Z"
}

// Self-Awareness System Status Response
{
    "type": "system_status_response",
    "status": "healthy",
    "metrics": {
        "audio_input_level": -12.5,
        "stt_confidence": 94.2,
        "llm_response_time": 1.2,
        "tts_success_rate": 100,
        "error_count": 0,
        "session_duration": 1847
    },
    "analysis": "All systems optimal. No performance degradation detected.",
    "recommendations": ["Continue current configuration"],
    "alerts": [],
    "timestamp": "2024-01-20T10:30:00Z"
}

// Self-Awareness Query (User asking about capabilities)
{
    "type": "self_awareness_query",
    "question": "Can you browse the web?",
    "context": {
        "conversation_turn": 5,
        "user_intent": "capability_assessment"
    },
    "timestamp": "2024-01-20T10:30:00Z"
}

// Self-Awareness Response with Capability Analysis
{
    "type": "self_awareness_response",
    "answer": "No live internet browsing capabilities. I can only access information from my training data and analyze system logs. No real-time web access available.",
    "capability_assessment": {
        "internet_access": false,
        "explanation": "No live internet browsing or real-time web access",
        "alternatives": ["Access training data knowledge", "Analyze local system logs"]
    },
    "confidence": 100,
    "timestamp": "2024-01-20T10:30:00Z"
}

// Proactive Alert from Self-Awareness Monitor
{
    "type": "proactive_alert",
    "severity": "warning",
    "category": "audio_quality",
    "message": "Detected degraded audio quality - consider checking microphone position",
    "metrics": {
        "audio_level": -45.2,
        "background_noise": -20.1,
        "stt_confidence_drop": 15.3
    },
    "recommendations": ["Reposition microphone", "Check for interference sources"],
    "timestamp": "2024-01-20T10:30:00Z"
}

// Error Analysis Request
{
    "type": "error_analysis_request",
    "error_logs": ["2024-01-20 10:29:45 ERROR: STT confidence dropped to 45%"],
    "timeframe_minutes": 5,
    "context": "During active conversation",
    "timestamp": "2024-01-20T10:30:00Z"
}

// Error Analysis Response with LLM Reasoning
{
    "type": "error_analysis_response",
    "analysis": "Background noise increased to -20dB causing STT confidence drop. Microphone input shows irregular patterns suggesting device interference.",
    "root_cause": "Audio device interference",
    "severity": "medium",
    "recommendations": ["Check microphone connection", "Switch audio input device", "Reduce background noise"],
    "predicted_resolution_time": "immediate",
    "timestamp": "2024-01-20T10:30:00Z"
}

// Model-specific response with provider context and self-awareness
{
    "type": "response",
    "text": "Hello! How can I help you today?",
    "provider": "openai",
    "model": "gpt-4o",
    "model_info": {
        "name": "GPT-4o",
        "cost_tier": "medium",
        "context_length": 128000
    },
    "system_context": {
        "response_time": 1.2,
        "system_health": "optimal",
        "confidence": 98.5
    },
    "timestamp": "2024-01-20T10:30:00Z"
}
```

## **Enhanced Multi-LLM & Model Troubleshooting Guide**

### Common Provider Issues

#### OpenAI Provider
```
❌ Error: "401 Unauthorized"
✅ Solution: Check OpenAI.key file contains valid API key starting with 'sk-proj-' or 'sk-'

❌ Error: "Rate limit exceeded"  
✅ Solution: Implement exponential backoff or upgrade OpenAI plan

❌ Error: "Model not found"
✅ Solution: Verify model name (o3-mini, gpt-4o, gpt-4) in provider config

❌ Error: "o3 model access denied"
✅ Solution: o3 models require special access - check OpenAI account tier

❌ Error: "Context length exceeded"
✅ Solution: Reduce conversation history or switch to model with larger context
```

#### Claude Provider
```
❌ Error: "Authentication failed"
✅ Solution: Ensure Claude.key contains valid Anthropic API key starting with 'sk-ant-'

❌ Error: "Model access denied"
✅ Solution: Verify Claude model access in Anthropic Console - some models require approval

❌ Error: "Message format invalid"
✅ Solution: Check conversation history format matches Claude API requirements

❌ Error: "Claude 3 Opus unavailable"
✅ Solution: Switch to Claude 3.5 Sonnet or check model availability status

❌ Error: "Rate limit for Claude 3 Haiku"
✅ Solution: Claude 3 Haiku has higher rate limits - verify usage tier
```

#### XAI Provider  
```
❌ Error: "Service unavailable"
✅ Solution: XAI API is in beta - check status at https://x.ai/

❌ Error: "API key invalid"
✅ Solution: Verify XAI.key format and account access

❌ Error: "Grok 2 not available"
✅ Solution: Switch to Grok 1.5 or Grok Beta model

❌ Error: "Context limit exceeded"
✅ Solution: Grok models have different context limits - check model specs
```

#### LM Studio Provider
```
❌ Error: "Connection refused"
✅ Solution: Start LM Studio server on localhost:1234

❌ Error: "No model loaded"
✅ Solution: Load a model in LM Studio interface before testing

❌ Error: "Model not compatible"
✅ Solution: Ensure loaded model supports chat completion format

❌ Error: "Server timeout"
✅ Solution: Large models (70B) need more time - increase timeout

❌ Error: "CUDA out of memory"
✅ Solution: Switch to smaller model or reduce context length
```

#### Ollama Provider
```
❌ Error: "Service not running"
✅ Solution: Start Ollama service: ollama serve

❌ Error: "Model not found: llama3.1:70b"
✅ Solution: Pull specific model: ollama pull llama3.1:70b

❌ Error: "Model not found: mistral:7b"
✅ Solution: Pull model: ollama pull mistral:7b

❌ Error: "Out of memory"
✅ Solution: Use smaller model like phi3:mini or add more RAM

❌ Error: "Model loading failed"
✅ Solution: Check disk space and model file integrity
```

### Enhanced Status Indicators
```
🟢 Green: Provider and model healthy and responding
🟡 Yellow: Provider/model testing or switching
🔴 Red: Provider/model error or unavailable  
⚪ White: Provider/model status unknown

Model Cost Indicators in Dropdown:
💚 Low cost/free tier models
🟡 Medium cost models  
🔴 High cost models
🆓 Free local models
```

### Enhanced Fallback Chain Logic with Model Selection
```
1. Try current selected provider with current model
2. If model fails, try default model for same provider
3. If provider fails, try OpenAI with gpt-4o (most reliable)
4. If fails, try Claude with claude-3-5-sonnet (high quality)
5. If fails, try LM Studio with auto-detect (local)
6. If fails, try Ollama with llama3.1:8b (fallback)
7. If all fail, show comprehensive error message with provider/model info
```

### Comprehensive Setup Checklist
```
□ All API key files created in keys/ directory (OpenAI.key, Claude.key, XAI.key)
□ .gitignore file protects keys/ directory
□ Local services started (LM Studio on :1234, Ollama on :11434)
□ Models downloaded for local providers (ollama pull llama3.1:8b)
□ Provider health checks pass for all configured providers
□ Model health checks pass for default models
□ Fallback chain tested with multiple provider/model combinations
□ UI dual dropdown functionality working (provider + model selection)
□ Status indicators updating correctly for both provider and model
□ WebSocket provider and model switching functional
□ Process logs showing current provider/model information
□ Model-specific error handling and recovery working
```

### Model Selection Best Practices
```
💡 Performance Optimization:
- Use o3-mini or gpt-3.5-turbo for fast responses
- Use gpt-4o or claude-3-5-sonnet for complex tasks
- Use local models (LM Studio/Ollama) for privacy

💡 Cost Optimization:
- Start with free tier: phi3:mini (Ollama) → gpt-3.5-turbo → claude-3-haiku  
- Production: gpt-4o → claude-3-5-sonnet → grok-2

💡 Reliability:
- Primary: OpenAI models (highest uptime)
- Secondary: Claude models (high quality backup)  
- Tertiary: Local models (always available offline)
```

### Self-Awareness UI Component Implementation
```javascript
// self-awareness-ui.js - Frontend interface for self-awareness monitor
class SelfAwarenessUI {
    constructor() {
        this.websocket = null;
        this.systemStatus = {};
        this.alertsContainer = null;
        this.metricsContainer = null;
        this.isVisible = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.startHealthChecking();
    }
    
    initializeElements() {
        // Create self-awareness UI panel
        this.createSelfAwarenessPanel();
        
        // Get references to UI elements
        this.alertsContainer = document.getElementById('selfAwarenessAlerts');
        this.metricsContainer = document.getElementById('selfAwarenessMetrics');
        this.toggleButton = document.getElementById('toggleSelfAwareness');
        this.refreshButton = document.getElementById('refreshSystemStatus');
    }
    
    createSelfAwarenessPanel() {
        const panelHTML = `
        <div id="selfAwarenessPanel" class="self-awareness-panel collapsed">
            <div class="panel-header">
                <h3>🧠 System Consciousness</h3>
                <button id="toggleSelfAwareness" class="toggle-btn">▼</button>
            </div>
            <div class="panel-content">
                <div class="metrics-section">
                    <h4>Real-time Metrics</h4>
                    <div id="selfAwarenessMetrics" class="metrics-grid">
                        <div class="metric-item">
                            <span class="metric-label">Audio Level:</span>
                            <span id="audioLevel" class="metric-value">--</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">STT Confidence:</span>
                            <span id="sttConfidence" class="metric-value">--</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Response Time:</span>
                            <span id="responseTime" class="metric-value">--</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">System Health:</span>
                            <span id="systemHealth" class="metric-value">--</span>
                        </div>
                    </div>
                </div>
                
                <div class="alerts-section">
                    <h4>System Alerts & Analysis</h4>
                    <div id="selfAwarenessAlerts" class="alerts-container">
                        <div class="alert-item info">
                            <span class="alert-time">--:--:--</span>
                            <span class="alert-message">System monitoring initialized</span>
                        </div>
                    </div>
                </div>
                
                <div class="actions-section">
                    <button id="refreshSystemStatus" class="action-btn">🔄 Refresh Status</button>
                    <button id="requestErrorAnalysis" class="action-btn">🔍 Analyze Errors</button>
                    <button id="testCapabilities" class="action-btn">🎯 Test Capabilities</button>
                </div>
            </div>
        </div>`;
        
        // Insert panel into the page
        document.body.insertAdjacentHTML('beforeend', panelHTML);
    }
    
    setupEventListeners() {
        // Toggle panel visibility
        this.toggleButton.addEventListener('click', () => {
            this.togglePanel();
        });
        
        // Refresh system status
        this.refreshButton.addEventListener('click', () => {
            this.requestSystemStatus();
        });
        
        // Request error analysis
        document.getElementById('requestErrorAnalysis').addEventListener('click', () => {
            this.requestErrorAnalysis();
        });
        
        // Test capabilities
        document.getElementById('testCapabilities').addEventListener('click', () => {
            this.testSystemCapabilities();
        });
        
        // Listen for WebSocket messages
        window.addEventListener('llmProviderChanged', (event) => {
            this.logAlert(`Switched to ${event.detail.providerName}`, 'info');
        });
    }
    
    setWebSocket(websocket) {
        this.websocket = websocket;
        
        // Listen for self-awareness messages
        websocket.addEventListener('message', (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        });
    }
    
    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'system_status_response':
                this.updateSystemMetrics(message);
                break;
            case 'self_awareness_response':
                this.displaySelfAwarenessResponse(message);
                break;
            case 'proactive_alert':
                this.displayProactiveAlert(message);
                break;
            case 'error_analysis_response':
                this.displayErrorAnalysis(message);
                break;
            case 'health_check_update':
                this.updateHealthStatus(message);
                break;
        }
    }
    
    togglePanel() {
        const panel = document.getElementById('selfAwarenessPanel');
        this.isVisible = !this.isVisible;
        
        if (this.isVisible) {
            panel.classList.remove('collapsed');
            this.toggleButton.textContent = '▲';
            this.requestSystemStatus(); // Refresh when opened
        } else {
            panel.classList.add('collapsed');
            this.toggleButton.textContent = '▼';
        }
    }
    
    requestSystemStatus() {
        if (!this.websocket) return;
        
        const message = {
            type: 'system_status_query',
            query_type: 'recent_performance',
            timeframe_minutes: 10,
            include_logs: true,
            include_predictions: true,
            timestamp: new Date().toISOString()
        };
        
        this.websocket.send(JSON.stringify(message));
        this.logAlert('Requesting system status...', 'info');
    }
    
    updateSystemMetrics(statusResponse) {
        const metrics = statusResponse.metrics;
        
        // Update metric displays
        document.getElementById('audioLevel').textContent = 
            `${metrics.audio_input_level || '--'} dB`;
        document.getElementById('sttConfidence').textContent = 
            `${metrics.stt_confidence || '--'}%`;
        document.getElementById('responseTime').textContent = 
            `${metrics.llm_response_time || '--'}s`;
        document.getElementById('systemHealth').textContent = 
            statusResponse.status || '--';
        
        // Update health status color
        const healthElement = document.getElementById('systemHealth');
        healthElement.className = `metric-value ${statusResponse.status}`;
        
        // Log analysis if provided
        if (statusResponse.analysis) {
            this.logAlert(statusResponse.analysis, 'success');
        }
        
        // Display recommendations
        if (statusResponse.recommendations && statusResponse.recommendations.length > 0) {
            statusResponse.recommendations.forEach(rec => {
                this.logAlert(`Recommendation: ${rec}`, 'info');
            });
        }
    }
    
    displayProactiveAlert(alert) {
        this.logAlert(alert.message, alert.severity);
        
        // If audio quality issue, also update VU meter warning
        if (alert.category === 'audio_quality' && window.vuMeter) {
            window.vuMeter.showWarning(alert.message);
        }
    }
    
    displayErrorAnalysis(analysis) {
        this.logAlert(`Error Analysis: ${analysis.analysis}`, 'warning');
        this.logAlert(`Root Cause: ${analysis.root_cause}`, 'error');
        
        analysis.recommendations.forEach(rec => {
            this.logAlert(`Fix: ${rec}`, 'info');
        });
    }
    
    requestErrorAnalysis() {
        if (!this.websocket) return;
        
        const message = {
            type: 'error_analysis_request',
            timeframe_minutes: 5,
            context: 'User requested analysis',
            timestamp: new Date().toISOString()
        };
        
        this.websocket.send(JSON.stringify(message));
        this.logAlert('Analyzing recent errors...', 'info');
    }
    
    testSystemCapabilities() {
        if (!this.websocket) return;
        
        const testQueries = [
            'Can you browse the web?',
            'Can you generate images?',
            'Is this working?',
            'Do you hear me clearly?'
        ];
        
        testQueries.forEach((query, index) => {
            setTimeout(() => {
                const message = {
                    type: 'self_awareness_query',
                    question: query,
                    context: {
                        conversation_turn: index + 1,
                        user_intent: 'capability_testing'
                    },
                    timestamp: new Date().toISOString()
                };
                
                this.websocket.send(JSON.stringify(message));
            }, index * 1000); // Stagger requests
        });
        
        this.logAlert('Testing system capabilities...', 'info');
    }
    
    logAlert(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const alertHTML = `
            <div class="alert-item ${type}">
                <span class="alert-time">${timestamp}</span>
                <span class="alert-message">${message}</span>
            </div>`;
        
        this.alertsContainer.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Keep only last 20 alerts
        const alerts = this.alertsContainer.children;
        if (alerts.length > 20) {
            this.alertsContainer.removeChild(alerts[alerts.length - 1]);
        }
    }
    
    startHealthChecking() {
        // Request system status every 30 seconds
        setInterval(() => {
            if (this.isVisible && this.websocket) {
                this.requestSystemStatus();
            }
        }, 30000);
    }
}

// CSS for Self-Awareness UI
const selfAwarenessCSS = `
.self-awareness-panel {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 400px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
    z-index: 1000;
    transition: all 0.3s ease;
}

.self-awareness-panel.collapsed .panel-content {
    display: none;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.panel-header h3 {
    margin: 0;
    color: #333;
    font-size: 16px;
}

.toggle-btn {
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    color: #666;
}

.panel-content {
    padding: 20px;
    max-height: 500px;
    overflow-y: auto;
}

.metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
}

.metric-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 12px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 8px;
}

.metric-label {
    font-weight: 500;
    color: #555;
}

.metric-value {
    font-weight: bold;
}

.metric-value.healthy { color: #28a745; }
.metric-value.degraded { color: #ffc107; }
.metric-value.error { color: #dc3545; }

.alerts-container {
    max-height: 200px;
    overflow-y: auto;
    margin-bottom: 15px;
}

.alert-item {
    display: flex;
    gap: 10px;
    padding: 8px 12px;
    margin-bottom: 5px;
    border-radius: 6px;
    font-size: 13px;
}

.alert-item.info {
    background: rgba(23, 162, 184, 0.1);
    border-left: 3px solid #17a2b8;
}

.alert-item.success {
    background: rgba(40, 167, 69, 0.1);
    border-left: 3px solid #28a745;
}

.alert-item.warning {
    background: rgba(255, 193, 7, 0.1);
    border-left: 3px solid #ffc107;
}

.alert-item.error {
    background: rgba(220, 53, 69, 0.1);
    border-left: 3px solid #dc3545;
}

.alert-time {
    color: #666;
    font-weight: 500;
    min-width: 60px;
}

.actions-section {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.action-btn {
    padding: 8px 12px;
    border: none;
    border-radius: 6px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s ease;
}

.action-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

@media (max-width: 768px) {
    .self-awareness-panel {
        width: calc(100vw - 40px);
        right: 20px;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}
`;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Inject CSS
    const style = document.createElement('style');
    style.textContent = selfAwarenessCSS;
    document.head.appendChild(style);
    
    // Initialize Self-Awareness UI
    window.selfAwarenessUI = new SelfAwarenessUI();
});
```

This comprehensive prompt eliminates the need for multiple iteration cycles and provides all the proven patterns from the working implementation, plus robust multi-LLM provider support, complete Self-Awareness Monitor system, and comprehensive troubleshooting guidance.

---

**This specification provides everything needed to build a production-ready Self-Aware Voice-to-Text AI Assistant from scratch. Each module can be developed independently, and the entire system is designed for maintainability, scalability, and robust operation.**