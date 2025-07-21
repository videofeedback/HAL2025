class WebSocketClient {
    constructor() {
        this.websocket = null;
        this.sessionId = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageHandlers = new Map();
        this.connectionListeners = [];
        
        this.setupMessageHandlers();
    }
    
    setupMessageHandlers() {
        // Default message handlers
        this.messageHandlers.set('connection_established', this.handleConnectionEstablished.bind(this));
        this.messageHandlers.set('pong', this.handlePong.bind(this));
        this.messageHandlers.set('error', this.handleError.bind(this));
        this.messageHandlers.set('transcription', this.handleTranscription.bind(this));
        this.messageHandlers.set('response', this.handleResponse.bind(this));
        this.messageHandlers.set('audio_response', this.handleAudioResponse.bind(this));
        this.messageHandlers.set('provider_changed', this.handleProviderChanged.bind(this));
        this.messageHandlers.set('model_changed', this.handleModelChanged.bind(this));
        this.messageHandlers.set('system_status_response', this.handleSystemStatusResponse.bind(this));
        this.messageHandlers.set('self_awareness_response', this.handleSelfAwarenessResponse.bind(this));
        this.messageHandlers.set('proactive_alert', this.handleProactiveAlert.bind(this));
        this.messageHandlers.set('error_analysis_response', this.handleErrorAnalysisResponse.bind(this));
    }
    
    async connect() {
        try {
            // Create session first
            const response = await fetch('/session', { method: 'POST' });
            const sessionData = await response.json();
            this.sessionId = sessionData.session_id;
            
            // Connect to WebSocket
            const wsUrl = `ws://${window.location.host}/ws/${this.sessionId}`; 
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = this.onOpen.bind(this);
            this.websocket.onmessage = this.onMessage.bind(this);
            this.websocket.onclose = this.onClose.bind(this);
            this.websocket.onerror = this.onError.bind(this);
            
            return new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Connection timeout'));
                }, 5000);
                
                this.websocket.onopen = () => {
                    clearTimeout(timeout);
                    this.onOpen();
                    resolve();
                };
                
                this.websocket.onerror = () => {
                    clearTimeout(timeout);
                    reject(new Error('Connection failed'));
                };
            });
            
        } catch (error) {
            console.error('Connection error:', error);
            throw error;
        }
    }
    
    onOpen() {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyConnectionListeners(true);
        
        // Start heartbeat
        this.startHeartbeat();
    }
    
    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            const handler = this.messageHandlers.get(message.type);
            
            if (handler) {
                handler(message);
            } else {
                console.warn('Unknown message type:', message.type);
            }
            
        } catch (error) {
            console.error('Error processing message:', error);
        }
    }
    
    onClose(event) {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.notifyConnectionListeners(false);
        
        // Stop heartbeat
        this.stopHeartbeat();
        
        // Attempt reconnection if not intentional
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
        }
    }
    
    onError(error) {
        console.error('WebSocket error:', error);
    }
    
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            this.connect().catch(error => {
                console.error('Reconnection failed:', error);
            });
        }, delay);
    }
    
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping' });
            }
        }, 30000); // Every 30 seconds
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    send(message) {
        if (this.isConnected && this.websocket) {
            this.websocket.send(JSON.stringify(message));
            return true;
        } else {
            console.warn('Cannot send message: not connected');
            return false;
        }
    }
    
    addMessageHandler(type, handler) {
        this.messageHandlers.set(type, handler);
    }
    
    removeMessageHandler(type) {
        this.messageHandlers.delete(type);
    }
    
    addConnectionListener(listener) {
        this.connectionListeners.push(listener);
    }
    
    notifyConnectionListeners(connected) {
        this.connectionListeners.forEach(listener => {
            try {
                listener(connected);
            } catch (error) {
                console.error('Connection listener error:', error);
            }
        });
    }
    
    async disconnect() {
        if (this.websocket) {
            this.stopHeartbeat();
            this.websocket.close(1000, 'User disconnect');
            
            // Delete session
            if (this.sessionId) {
                try {
                    await fetch(`/session/${this.sessionId}`, { method: 'DELETE' });
                } catch (error) {
                    console.error('Error deleting session:', error);
                }
            }
        }
    }
    
    // Message Handlers
    handleConnectionEstablished(message) {
        console.log('Connection established:', message);
        this.dispatchEvent('connectionEstablished', message);
    }
    
    handlePong(message) {
        // Heartbeat response - connection is alive
    }
    
    handleError(message) {
        console.error('Server error:', message.message);
        this.dispatchEvent('serverError', message);
    }
    
    handleTranscription(message) {
        this.dispatchEvent('transcription', message);
    }
    
    handleResponse(message) {
        this.dispatchEvent('response', message);
    }
    
    handleAudioResponse(message) {
        this.dispatchEvent('audioResponse', message);
    }
    
    handleProviderChanged(message) {
        console.log('Provider changed:', message);
        this.dispatchEvent('providerChanged', message);
    }
    
    handleModelChanged(message) {
        console.log('Model changed:', message);
        this.dispatchEvent('modelChanged', message);
    }
    
    handleSystemStatusResponse(message) {
        this.dispatchEvent('systemStatusResponse', message);
    }
    
    handleSelfAwarenessResponse(message) {
        this.dispatchEvent('selfAwarenessResponse', message);
    }
    
    handleProactiveAlert(message) {
        console.warn('Proactive alert:', message);
        this.dispatchEvent('proactiveAlert', message);
    }
    
    handleErrorAnalysisResponse(message) {
        this.dispatchEvent('errorAnalysisResponse', message);
    }
    
    // Event dispatching
    dispatchEvent(eventType, data) {
        const event = new CustomEvent(eventType, { detail: data });
        window.dispatchEvent(event);
    }
    
    // API Methods
    sendAudioData(audioData) {
        return this.send({
            type: 'audio_data',
            data: audioData,
            timestamp: new Date().toISOString()
        });
    }
    
    sendTextInput(text) {
        return this.send({
            type: 'text_input',
            text: text,
            timestamp: new Date().toISOString()
        });
    }
    
    changeProvider(provider, model = null) {
        return this.send({
            type: 'change_provider',
            provider: provider,
            model: model,
            timestamp: new Date().toISOString()
        });
    }
    
    changeModel(model, provider = null) {
        return this.send({
            type: 'change_model',
            model: model,
            provider: provider,
            timestamp: new Date().toISOString()
        });
    }
    
    requestSystemStatus(queryType = 'current', timeframeMinutes = 10) {
        return this.send({
            type: 'system_status_query',
            query_type: queryType,
            timeframe_minutes: timeframeMinutes,
            include_logs: true,
            include_predictions: true,
            timestamp: new Date().toISOString()
        });
    }
    
    askSelfAwareness(question, context = {}) {
        return this.send({
            type: 'self_awareness_query',
            question: question,
            context: {
                conversation_turn: context.turn || 1,
                user_intent: context.intent || 'general_query',
                ...context
            },
            timestamp: new Date().toISOString()
        });
    }
    
    requestErrorAnalysis(timeframeMinutes = 5) {
        return this.send({
            type: 'error_analysis_request',
            timeframe_minutes: timeframeMinutes,
            context: 'User requested analysis',
            timestamp: new Date().toISOString()
        });
    }
}

// Global WebSocket client instance
window.wsClient = new WebSocketClient();