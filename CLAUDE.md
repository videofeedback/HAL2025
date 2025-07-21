# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a specification for building a **Self-Aware Voice-Activated AI Assistant** called "OneShotTTSprompt v2.0". This is a comprehensive design document rather than an implemented codebase.

## Key Document Structure

The main specification is in `OneShotTTSprompt_v2.md` which defines:

### Core Architecture Requirements
- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: Vanilla JavaScript (ES6+) 
- **Audio Processing**: OpenAI Whisper + macOS TTS
- **Local LLM**: Ollama (llama3.1:8b-instruct)
- **Communication**: WebSocket real-time bidirectional
- **Platform**: macOS (TTS dependency)

### Multi-LLM Provider Support
The system supports multiple LLM providers with automatic fallback:
- OpenAI (GPT-4o, o3-mini, gpt-3.5-turbo)
- Claude (claude-3-5-sonnet, claude-3-haiku)
- XAI (Grok models)
- LM Studio (local models on localhost:1234)
- Ollama (local models on localhost:11434)

### Self-Awareness Monitor System
A dedicated local LLM provides system consciousness:
- Real-time log analysis and error detection
- Capability assessment and limitation awareness
- Proactive alerts and performance monitoring
- Intelligent error diagnosis with LLM reasoning

## Modular Implementation Strategy

The specification defines 6 main modules for independent development:

1. **Core System Foundation** - FastAPI server with WebSocket communication
2. **Audio Processing Pipeline** - Speech-to-text and text-to-speech handling
3. **Multi-LLM Provider System** - Unified interface with automatic fallback
4. **Self-Awareness Monitor** - Dedicated local LLM for system consciousness
5. **Frontend Interface** - Voice interaction controls and system monitoring
6. **Integration & Communication** - WebSocket messaging between modules

## Dependencies and Setup Requirements

### Prerequisites
```bash
# Required system dependencies
brew install ffmpeg
brew install ollama
pip install fastapi uvicorn websockets openai-whisper openai anthropic aiohttp torch torchaudio
```

### API Keys Required
```bash
# Create these files in config/keys/
config/keys/OpenAI.key          # OpenAI API key (sk-proj-...)
config/keys/Claude.key          # Anthropic API key (sk-ant-...)
config/keys/XAI.key             # XAI API key (optional)
```

### Local Services
```bash
# Start Ollama service
ollama serve

# Pull required model for self-awareness
ollama pull llama3.1:8b-instruct
```

## Implementation Phases

The document outlines a 6-phase implementation strategy:
1. Foundation setup (FastAPI + WebSocket)
2. Audio pipeline (Whisper + macOS TTS)
3. LLM integration (multi-provider system)
4. Self-awareness monitor (local LLM consciousness)
5. Frontend interface (voice controls + monitoring)
6. Integration and testing

## Validation and Testing

Each module includes specific validation criteria and the document provides:
- Performance benchmarks (transcription < 2s, LLM response < 3s, TTS < 1s)
- Comprehensive troubleshooting guide for each LLM provider
- End-to-end workflow testing procedures

## Key Design Patterns

- **Provider abstraction**: Base class interface for all LLM providers
- **Fallback chains**: Automatic provider switching on failure
- **Self-monitoring**: Local LLM analyzes system logs and performance
- **WebSocket messaging**: Standardized communication protocol between modules
- **Modular architecture**: Independent development and testing of components

## Notes for Implementation

- This is currently a specification document, not implemented code
- The system is designed for macOS due to TTS dependencies
- Local LLM integration provides offline fallback capabilities
- Self-awareness features enable intelligent error handling and user interaction
- UI styling will be applied from a referenced template.png image