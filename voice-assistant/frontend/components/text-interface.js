class TextInterface {
    constructor() {
        this.textInput = null;
        this.sendButton = null;
        this.isProcessing = false;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.textInput = document.getElementById('textInput');
        this.sendButton = document.getElementById('sendTextButton');
    }
    
    setupEventListeners() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', this.sendTextMessage.bind(this));
        }
        
        if (this.textInput) {
            // Send on Enter (but not Shift+Enter for multiline)
            this.textInput.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    this.sendTextMessage();
                }
            });
            
            // Enable/disable send button based on input
            this.textInput.addEventListener('input', this.updateSendButton.bind(this));
        }
        
        // Listen for WebSocket events
        window.addEventListener('connectionEstablished', this.onConnectionEstablished.bind(this));
        window.addEventListener('response', this.handleResponse.bind(this));
        window.addEventListener('serverError', this.handleError.bind(this));
    }
    
    onConnectionEstablished() {
        this.updateSendButton();
    }
    
    updateSendButton() {
        if (this.sendButton && this.textInput) {
            const hasText = this.textInput.value.trim().length > 0;
            const isConnected = window.wsClient && window.wsClient.isConnected;
            this.sendButton.disabled = !hasText || !isConnected || this.isProcessing;
        }
    }
    
    async sendTextMessage() {
        if (!this.textInput || !this.sendButton) return;
        
        const text = this.textInput.value.trim();
        if (!text) return;
        
        if (!window.wsClient || !window.wsClient.isConnected) {
            this.showError('Not connected to server');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.updateSendButton();
            this.updateUI(true);
            
            // Send text input to server
            window.wsClient.sendTextInput(text);
            
            // Clear input
            this.textInput.value = '';
            
            // Show feedback
            if (window.selfAwarenessUI) {
                window.selfAwarenessUI.logAlert(`Text sent: ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`, 'info');
            }
            
        } catch (error) {
            console.error('Error sending text:', error);
            this.showError('Failed to send message: ' + error.message);
        }
    }
    
    handleResponse(event) {
        this.isProcessing = false;
        this.updateSendButton();
        this.updateUI(false);
        
        const data = event.detail;
        console.log('Text response received:', data);
        
        // Response will be handled by ResponseDisplay component
    }
    
    handleError(event) {
        this.isProcessing = false;
        this.updateSendButton();
        this.updateUI(false);
        
        const error = event.detail || event;
        this.showError(error.message || 'Unknown error occurred');
    }
    
    updateUI(processing) {
        if (this.textInput) {
            this.textInput.disabled = processing;
            if (processing) {
                this.textInput.placeholder = 'Processing...';
            } else {
                this.textInput.placeholder = 'Type your message here as an alternative to voice input...';
            }
        }
        
        if (this.sendButton) {
            if (processing) {
                this.sendButton.textContent = 'Sending...';
            } else {
                this.sendButton.textContent = 'Send';
            }
        }
    }
    
    showError(message) {
        console.error('Text interface error:', message);
        
        if (window.selfAwarenessUI) {
            window.selfAwarenessUI.logAlert(`Text input error: ${message}`, 'error');
        }
        
        // Could also show inline error message
        this.showInlineMessage(message, 'error');
    }
    
    showInlineMessage(message, type = 'info') {
        // Remove existing message
        const existingMessage = document.querySelector('.text-interface-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Create new message
        const messageElement = document.createElement('div');
        messageElement.className = `text-interface-message ${type}`;
        messageElement.textContent = message;
        messageElement.style.cssText = `
            margin-top: 10px;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9em;
            background: ${type === 'error' ? 'rgba(220, 53, 69, 0.1)' : 'rgba(23, 162, 184, 0.1)'};
            color: ${type === 'error' ? '#dc3545' : '#17a2b8'};
            border-left: 3px solid ${type === 'error' ? '#dc3545' : '#17a2b8'};
        `;
        
        // Insert after text input container
        const container = this.textInput.closest('.text-input-container');
        if (container && container.parentNode) {
            container.parentNode.insertBefore(messageElement, container.nextSibling);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 5000);
        }
    }
    
    // Public methods
    setEnabled(enabled) {
        if (this.textInput) {
            this.textInput.disabled = !enabled;
        }
        this.updateSendButton();
    }
    
    setText(text) {
        if (this.textInput) {
            this.textInput.value = text;
            this.updateSendButton();
        }
    }
    
    getText() {
        return this.textInput ? this.textInput.value : '';
    }
    
    clear() {
        if (this.textInput) {
            this.textInput.value = '';
            this.updateSendButton();
        }
    }
    
    focus() {
        if (this.textInput) {
            this.textInput.focus();
        }
    }
}

// Initialize text interface when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.textInterface = new TextInterface();
});