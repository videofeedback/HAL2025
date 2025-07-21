class ProviderSelector {
    constructor() {
        this.providers = {};
        this.currentProvider = null;
        this.currentModel = null;
        
        this.providerSelect = null;
        this.modelSelect = null;
        this.providerStatus = null;
        this.modelStatus = null;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.providerSelect = document.getElementById('providerSelect');
        this.modelSelect = document.getElementById('modelSelect');
        this.providerStatus = document.getElementById('providerStatus');
        this.modelStatus = document.getElementById('modelStatus');
    }
    
    setupEventListeners() {
        if (this.providerSelect) {
            this.providerSelect.addEventListener('change', this.handleProviderChange.bind(this));
        }
        
        if (this.modelSelect) {
            this.modelSelect.addEventListener('change', this.handleModelChange.bind(this));
        }
        
        // Listen for WebSocket events
        window.addEventListener('connectionEstablished', this.onConnectionEstablished.bind(this));
        window.addEventListener('providerChanged', this.handleProviderChanged.bind(this));
        window.addEventListener('modelChanged', this.handleModelChanged.bind(this));
        window.addEventListener('serverError', this.handleError.bind(this));
    }
    
    async onConnectionEstablished() {
        await this.loadProviderStatus();
    }
    
    async loadProviderStatus() {
        try {
            const response = await fetch('/providers/status');
            const data = await response.json();
            
            this.providers = data.providers;
            this.populateProviderDropdown();
            this.setDefaultProvider();
            
        } catch (error) {
            console.error('Error loading provider status:', error);
            this.showError('Failed to load provider information');
        }
    }
    
    populateProviderDropdown() {
        if (!this.providerSelect) return;
        
        // Clear existing options
        this.providerSelect.innerHTML = '<option value="">Select Provider</option>';
        
        // Add provider options
        Object.keys(this.providers).forEach(providerName => {
            const provider = this.providers[providerName];
            const option = document.createElement('option');
            option.value = providerName;
            option.textContent = this.getProviderDisplayName(providerName);
            
            // Disable if not available
            if (!provider.available) {
                option.disabled = true;
                option.textContent += ' (Not Available)';
            }
            
            this.providerSelect.appendChild(option);
        });
        
        // Enable the dropdown
        this.providerSelect.disabled = false;
    }
    
    populateModelDropdown(providerName) {
        if (!this.modelSelect || !providerName || !this.providers[providerName]) {
            this.clearModelDropdown();
            return;
        }
        
        const provider = this.providers[providerName];
        
        // Clear existing options
        this.modelSelect.innerHTML = '<option value="">Select Model</option>';
        
        // Add model options
        provider.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = this.getModelDisplayName(model);
            
            // Disable if not available
            if (!model.available) {
                option.disabled = true;
                option.textContent += ' (Not Available)';
            }
            
            // Mark current model as selected
            if (model.id === provider.current_model) {
                option.selected = true;
            }
            
            this.modelSelect.appendChild(option);
        });
        
        // Enable the dropdown
        this.modelSelect.disabled = false;
    }
    
    clearModelDropdown() {
        if (this.modelSelect) {
            this.modelSelect.innerHTML = '<option value="">Select Provider First</option>';
            this.modelSelect.disabled = true;
        }
    }
    
    setDefaultProvider() {
        // Find first available provider
        const availableProviders = Object.keys(this.providers).filter(name => 
            this.providers[name].available
        );
        
        if (availableProviders.length > 0) {
            const defaultProvider = availableProviders[0];
            this.selectProvider(defaultProvider);
        }
    }
    
    selectProvider(providerName) {
        if (this.providerSelect) {
            this.providerSelect.value = providerName;
        }
        
        this.currentProvider = providerName;
        this.populateModelDropdown(providerName);
        this.updateProviderStatus(providerName);
        
        // Auto-select current model
        if (providerName && this.providers[providerName]) {
            const currentModel = this.providers[providerName].current_model;
            if (currentModel) {
                this.selectModel(currentModel);
            }
        }
    }
    
    selectModel(modelId) {
        if (this.modelSelect) {
            this.modelSelect.value = modelId;
        }
        
        this.currentModel = modelId;
        this.updateModelStatus(modelId);
    }
    
    handleProviderChange() {
        const selectedProvider = this.providerSelect.value;
        
        if (selectedProvider && selectedProvider !== this.currentProvider) {
            this.changeProvider(selectedProvider);
        } else if (!selectedProvider) {
            this.clearModelDropdown();
            this.currentProvider = null;
            this.currentModel = null;
            this.updateProviderStatus(null);
            this.updateModelStatus(null);
        }
    }
    
    handleModelChange() {
        const selectedModel = this.modelSelect.value;
        
        if (selectedModel && selectedModel !== this.currentModel) {
            this.changeModel(selectedModel);
        } else if (!selectedModel) {
            this.currentModel = null;
            this.updateModelStatus(null);
        }
    }
    
    async changeProvider(providerName) {
        try {
            if (!window.wsClient || !window.wsClient.isConnected) {
                throw new Error('Not connected to server');
            }
            
            // Send provider change request
            window.wsClient.changeProvider(providerName);
            
            // Update UI immediately (will be confirmed by server response)
            this.selectProvider(providerName);
            
            if (window.selfAwarenessUI) {
                window.selfAwarenessUI.logAlert(`Changing provider to ${providerName}...`, 'info');
            }
            
        } catch (error) {
            console.error('Error changing provider:', error);
            this.showError('Failed to change provider: ' + error.message);
            
            // Revert selection
            this.providerSelect.value = this.currentProvider || '';
        }
    }
    
    async changeModel(modelId) {
        try {
            if (!window.wsClient || !window.wsClient.isConnected) {
                throw new Error('Not connected to server');
            }
            
            // Send model change request
            window.wsClient.changeModel(modelId, this.currentProvider);
            
            // Update UI immediately (will be confirmed by server response)
            this.selectModel(modelId);
            
            if (window.selfAwarenessUI) {
                window.selfAwarenessUI.logAlert(`Changing model to ${modelId}...`, 'info');
            }
            
        } catch (error) {
            console.error('Error changing model:', error);
            this.showError('Failed to change model: ' + error.message);
            
            // Revert selection
            this.modelSelect.value = this.currentModel || '';
        }
    }
    
    handleProviderChanged(event) {
        const data = event.detail;
        console.log('Provider changed confirmation:', data);
        
        this.currentProvider = data.provider;
        this.currentModel = data.model;
        
        // Update UI to reflect server state
        this.selectProvider(data.provider);
        if (data.model) {
            this.selectModel(data.model);
        }
        
        if (window.selfAwarenessUI) {
            window.selfAwarenessUI.logAlert(`Provider changed to ${data.provider}`, 'success');
        }
    }
    
    handleModelChanged(event) {
        const data = event.detail;
        console.log('Model changed confirmation:', data);
        
        this.currentModel = data.model;
        this.currentProvider = data.provider;
        
        // Update UI to reflect server state
        this.selectModel(data.model);
        
        if (window.selfAwarenessUI) {
            window.selfAwarenessUI.logAlert(`Model changed to ${data.model}`, 'success');
        }
    }
    
    updateProviderStatus(providerName) {
        if (!this.providerStatus) return;
        
        if (!providerName || !this.providers[providerName]) {
            this.providerStatus.textContent = '⚪';
            this.providerStatus.title = 'No provider selected';
            return;
        }
        
        const provider = this.providers[providerName];
        
        if (provider.available && provider.model_health) {
            this.providerStatus.textContent = '🟢';
            this.providerStatus.title = 'Provider healthy and available';
        } else if (provider.available) {
            this.providerStatus.textContent = '🟡';
            this.providerStatus.title = 'Provider available but model health unknown';
        } else {
            this.providerStatus.textContent = '🔴';
            this.providerStatus.title = 'Provider not available';
        }
    }
    
    updateModelStatus(modelId) {
        if (!this.modelStatus) return;
        
        if (!modelId || !this.currentProvider) {
            this.modelStatus.textContent = '⚪';
            this.modelStatus.title = 'No model selected';
            return;
        }
        
        const provider = this.providers[this.currentProvider];
        const model = provider.models.find(m => m.id === modelId);
        
        if (model && model.available) {
            this.modelStatus.textContent = '🟢';
            this.modelStatus.title = 'Model available';
        } else {
            this.modelStatus.textContent = '🔴';
            this.modelStatus.title = 'Model not available';
        }
    }
    
    getProviderDisplayName(providerName) {
        const displayNames = {
            'openai': 'OpenAI',
            'claude': 'Claude (Anthropic)',
            'xai': 'XAI (Grok)',
            'lm_studio': 'LM Studio',
            'ollama': 'Ollama (Local)'
        };
        return displayNames[providerName] || providerName;
    }
    
    getModelDisplayName(model) {
        let displayName = model.name || model.id;
        
        // Add cost indicator
        if (model.cost_tier) {
            const costIndicators = {
                'free': '🆓',
                'low': '💚',
                'medium': '🟡',
                'high': '🔴'
            };
            displayName = `${costIndicators[model.cost_tier] || ''} ${displayName}`;
        }
        
        return displayName;
    }
    
    showError(message) {
        console.error('Provider selector error:', message);
        
        if (window.selfAwarenessUI) {
            window.selfAwarenessUI.logAlert(`Provider error: ${message}`, 'error');
        }
    }
    
    handleError(event) {
        const error = event.detail || event;
        this.showError(error.message || 'Unknown error occurred');
    }
    
    // Public methods
    getCurrentProvider() {
        return this.currentProvider;
    }
    
    getCurrentModel() {
        return this.currentModel;
    }
    
    getProviders() {
        return { ...this.providers };
    }
    
    async refreshProviderStatus() {
        await this.loadProviderStatus();
    }
    
    setEnabled(enabled) {
        if (this.providerSelect) {
            this.providerSelect.disabled = !enabled;
        }
        if (this.modelSelect) {
            this.modelSelect.disabled = !enabled;
        }
    }
}

// Initialize provider selector when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.providerSelector = new ProviderSelector();
});