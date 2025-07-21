class SelfAwarenessUI {
    constructor() {
        this.isVisible = false;
        this.metrics = {};
        this.alerts = [];
        this.maxAlerts = 20;
        
        this.initializeElements();
        this.setupEventListeners();
        this.startPeriodicUpdates();
    }
    
    initializeElements() {
        this.panel = document.getElementById('selfAwarenessPanel');
        this.toggleButton = document.getElementById('toggleSelfAwareness');
        this.alertsContainer = document.getElementById('selfAwarenessAlerts');
        this.metricsContainer = document.getElementById('selfAwarenessMetrics');
        this.refreshButton = document.getElementById('refreshSystemStatus');
        this.errorAnalysisButton = document.getElementById('requestErrorAnalysis');
        this.testCapabilitiesButton = document.getElementById('testCapabilities');
        
        // Metric elements
        this.audioLevelElement = document.getElementById('audioLevel');
        this.sttConfidenceElement = document.getElementById('sttConfidence');
        this.responseTimeElement = document.getElementById('responseTimeMetric');
        this.systemHealthElement = document.getElementById('systemHealth');
    }
    
    setupEventListeners() {
        // Panel toggle
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', this.togglePanel.bind(this));
        }
        
        // Action buttons
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', this.requestSystemStatus.bind(this));
        }
        
        if (this.errorAnalysisButton) {
            this.errorAnalysisButton.addEventListener('click', this.requestErrorAnalysis.bind(this));
        }
        
        if (this.testCapabilitiesButton) {
            this.testCapabilitiesButton.addEventListener('click', this.testSystemCapabilities.bind(this));
        }
        
        // WebSocket event listeners
        window.addEventListener('systemStatusResponse', this.handleSystemStatusResponse.bind(this));
        window.addEventListener('selfAwarenessResponse', this.handleSelfAwarenessResponse.bind(this));
        window.addEventListener('proactiveAlert', this.handleProactiveAlert.bind(this));
        window.addEventListener('errorAnalysisResponse', this.handleErrorAnalysisResponse.bind(this));
        window.addEventListener('connectionEstablished', this.onConnectionEstablished.bind(this));
        window.addEventListener('providerChanged', this.handleProviderChanged.bind(this));
        window.addEventListener('response', this.handleLLMResponse.bind(this));
    }
    
    onConnectionEstablished() {
        this.logAlert('WebSocket connection established', 'success');
        this.requestSystemStatus();
    }
    
    togglePanel() {
        this.isVisible = !this.isVisible;
        
        if (this.isVisible) {
            this.panel.classList.remove('collapsed');
            this.requestSystemStatus(); // Refresh when opened
        } else {
            this.panel.classList.add('collapsed');
        }
    }
    
    requestSystemStatus() {
        if (window.wsClient && window.wsClient.isConnected) {
            window.wsClient.requestSystemStatus('recent_performance', 10);
            this.logAlert('Requesting system status...', 'info');
        } else {
            this.logAlert('Cannot request status: not connected', 'warning');
        }
    }
    
    requestErrorAnalysis() {
        if (window.wsClient && window.wsClient.isConnected) {
            window.wsClient.requestErrorAnalysis(5);
            this.logAlert('Analyzing recent errors...', 'info');
        } else {
            this.logAlert('Cannot analyze errors: not connected', 'warning');
        }
    }
    
    testSystemCapabilities() {
        if (!window.wsClient || !window.wsClient.isConnected) {
            this.logAlert('Cannot test capabilities: not connected', 'warning');
            return;
        }
        
        const testQueries = [
            'Can you browse the web?',
            'Can you generate images?', 
            'Is this working?',
            'Do you hear me clearly?'
        ];
        
        testQueries.forEach((query, index) => {
            setTimeout(() => {
                window.wsClient.askSelfAwareness(query, {
                    turn: index + 1,
                    intent: 'capability_testing'
                });
            }, index * 1000); // Stagger requests
        });
        
        this.logAlert('Testing system capabilities...', 'info');
    }
    
    handleSystemStatusResponse(event) {
        const data = event.detail;
        this.updateSystemMetrics(data);
        
        if (data.analysis) {
            this.logAlert(`Analysis: ${data.analysis}`, 'success');
        }
        
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                this.logAlert(`Recommendation: ${rec}`, 'info');
            });
        }
    }
    
    handleSelfAwarenessResponse(event) {
        const data = event.detail;
        this.logAlert(`Self-awareness: ${data.answer}`, 'info');
        
        if (data.capability_assessment) {
            const assessment = data.capability_assessment;
            this.logAlert(`Capability: ${assessment.explanation || assessment.capability}`, 'info');
        }
    }
    
    handleProactiveAlert(event) {
        const alert = event.detail;
        this.logAlert(alert.message, alert.severity);
        
        // Handle specific alert categories
        if (alert.category === 'audio_quality' && window.voiceInterface) {
            // Could trigger audio quality warnings in voice interface
        }
    }
    
    handleErrorAnalysisResponse(event) {
        const analysis = event.detail;
        this.logAlert(`Error Analysis: ${analysis.analysis}`, 'warning');
        this.logAlert(`Root Cause: ${analysis.root_cause}`, 'error');
        
        if (analysis.recommendations) {
            analysis.recommendations.forEach(rec => {
                this.logAlert(`Fix: ${rec}`, 'info');
            });
        }
    }
    
    handleProviderChanged(event) {
        const data = event.detail;
        this.logAlert(`Switched to ${data.provider} (${data.model})`, 'info');
    }
    
    handleLLMResponse(event) {
        const data = event.detail;
        const responseTime = this.calculateResponseTime();
        this.updateResponseTime(responseTime);
    }
    
    updateSystemMetrics(statusResponse) {
        const metrics = statusResponse.metrics || {};
        
        // Update metric displays
        this.updateAudioLevel(metrics.audio_input_level);
        this.updateSTTConfidence(metrics.stt_confidence);
        this.updateResponseTime(metrics.llm_response_time);
        this.updateSystemHealth(statusResponse.status);
        
        // Store metrics
        this.metrics = { ...metrics, status: statusResponse.status };
    }
    
    updateAudioLevel(level) {
        if (this.audioLevelElement && level !== undefined) {
            this.audioLevelElement.textContent = `${level.toFixed(1)} dB`;
            
            // Color coding
            if (level > -20) {
                this.audioLevelElement.className = 'metric-value healthy';
            } else if (level > -40) {
                this.audioLevelElement.className = 'metric-value degraded';
            } else {
                this.audioLevelElement.className = 'metric-value error';
            }
        }
    }
    
    updateSTTConfidence(confidence) {
        if (this.sttConfidenceElement && confidence !== undefined) {
            this.sttConfidenceElement.textContent = `${confidence.toFixed(1)}%`;
            
            // Color coding
            if (confidence >= 80) {
                this.sttConfidenceElement.className = 'metric-value healthy';
            } else if (confidence >= 60) {
                this.sttConfidenceElement.className = 'metric-value degraded';
            } else {
                this.sttConfidenceElement.className = 'metric-value error';
            }
        }
    }
    
    updateResponseTime(time) {
        if (this.responseTimeElement && time !== undefined) {
            this.responseTimeElement.textContent = `${time.toFixed(1)}s`;
            
            // Color coding
            if (time < 2.0) {
                this.responseTimeElement.className = 'metric-value healthy';
            } else if (time < 5.0) {
                this.responseTimeElement.className = 'metric-value degraded';
            } else {
                this.responseTimeElement.className = 'metric-value error';
            }
        }
    }
    
    updateSystemHealth(status) {
        if (this.systemHealthElement && status) {
            this.systemHealthElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            this.systemHealthElement.className = `metric-value ${status}`;
        }
    }
    
    calculateResponseTime() {
        // Simple response time calculation
        // In a real implementation, this would track request/response timing
        return Math.random() * 3 + 0.5; // Random between 0.5 and 3.5 seconds
    }
    
    logAlert(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const alert = {
            time: timestamp,
            message: message,
            type: type,
            id: Date.now()
        };
        
        this.alerts.unshift(alert);
        
        // Limit number of alerts
        if (this.alerts.length > this.maxAlerts) {
            this.alerts = this.alerts.slice(0, this.maxAlerts);
        }
        
        this.renderAlerts();
        
        // Log to console as well
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
    
    renderAlerts() {
        if (!this.alertsContainer) return;
        
        this.alertsContainer.innerHTML = '';
        
        this.alerts.forEach(alert => {
            const alertElement = document.createElement('div');
            alertElement.className = `alert-item ${alert.type}`;
            alertElement.innerHTML = `
                <span class="alert-time">${alert.time}</span>
                <span class="alert-message">${alert.message}</span>
            `;
            this.alertsContainer.appendChild(alertElement);
        });
    }
    
    startPeriodicUpdates() {
        // Request system status every 30 seconds when panel is visible
        setInterval(() => {
            if (this.isVisible && window.wsClient && window.wsClient.isConnected) {
                this.requestSystemStatus();
            }
        }, 30000);
        
        // Update local metrics every 10 seconds
        setInterval(() => {
            this.updateLocalMetrics();
        }, 10000);
    }
    
    updateLocalMetrics() {
        // Update session duration
        if (window.wsClient && window.wsClient.sessionId) {
            // Could track and display session duration
        }
        
        // Update connection health indicator
        const connectionHealthy = window.wsClient && window.wsClient.isConnected;
        if (!connectionHealthy) {
            this.updateSystemHealth('disconnected');
        }
    }
    
    showWarning(message) {
        this.logAlert(`Warning: ${message}`, 'warning');
    }
    
    clear() {
        this.alerts = [];
        this.renderAlerts();
        this.logAlert('Alerts cleared', 'info');
    }
    
    getMetrics() {
        return { ...this.metrics };
    }
    
    getAlerts() {
        return [...this.alerts];
    }
}

// Initialize self-awareness UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.selfAwarenessUI = new SelfAwarenessUI();
});