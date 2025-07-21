class VoiceInterface {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.audioChunks = [];
        this.vuMeterInterval = null;
        this.audioContext = null;
        this.analyser = null;
        
        this.recordButton = null;
        this.transcriptionText = null;
        this.transcriptionConfidence = null;
        this.vuLevel = null;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.recordButton = document.getElementById('recordButton');
        this.transcriptionText = document.getElementById('transcriptionText');
        this.transcriptionConfidence = document.getElementById('transcriptionConfidence');
        this.vuLevel = document.getElementById('vuLevel');
    }
    
    setupEventListeners() {
        if (this.recordButton) {
            this.recordButton.addEventListener('click', this.toggleRecording.bind(this));
        }
        
        // Listen for WebSocket events
        window.addEventListener('transcription', this.handleTranscription.bind(this));
        window.addEventListener('connectionEstablished', this.onConnectionEstablished.bind(this));
        window.addEventListener('serverError', this.handleError.bind(this));
    }
    
    onConnectionEstablished() {
        this.recordButton.disabled = false;
        this.updateTranscription('Ready to listen...', null);
    }
    
    async toggleRecording() {
        if (this.isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    async startRecording() {
        try {
            // Request microphone access
            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                }
            });
            
            // Setup audio context for VU meter
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = this.audioContext.createMediaStreamSource(this.audioStream);
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            source.connect(this.analyser);
            
            // Setup media recorder
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecordedAudio();
            };
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            this.updateRecordingUI(true);
            this.startVUMeter();
            this.updateTranscription('Listening...', null);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.handleError({ message: 'Microphone access failed: ' + error.message });
        }
    }
    
    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Clean up
            if (this.audioStream) {
                this.audioStream.getTracks().forEach(track => track.stop());
                this.audioStream = null;
            }
            
            if (this.audioContext) {
                this.audioContext.close();
                this.audioContext = null;
            }
            
            // Update UI
            this.updateRecordingUI(false);
            this.stopVUMeter();
            this.updateTranscription('Processing...', null);
        }
    }
    
    processRecordedAudio() {
        if (this.audioChunks.length > 0) {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            
            // Convert to base64 for transmission
            const reader = new FileReader();
            reader.onload = () => {
                const base64Audio = reader.result.split(',')[1];
                
                // Send to server via WebSocket
                if (window.wsClient && window.wsClient.isConnected) {
                    window.wsClient.sendAudioData(base64Audio);
                } else {
                    this.handleError({ message: 'Not connected to server' });
                }
            };
            reader.readAsDataURL(audioBlob);
        }
    }
    
    updateRecordingUI(recording) {
        if (recording) {
            this.recordButton.classList.add('recording');
            this.recordButton.querySelector('.record-text').textContent = 'Recording...';
            this.recordButton.querySelector('.record-icon').textContent = '⏹️';
        } else {
            this.recordButton.classList.remove('recording');
            this.recordButton.querySelector('.record-text').textContent = 'Click to Record';
            this.recordButton.querySelector('.record-icon').textContent = '🎤';
        }
    }
    
    startVUMeter() {
        if (this.analyser && this.vuLevel) {
            this.vuMeterInterval = setInterval(() => {
                const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
                this.analyser.getByteFrequencyData(dataArray);
                
                // Calculate average volume
                let sum = 0;
                for (let i = 0; i < dataArray.length; i++) {
                    sum += dataArray[i];
                }
                const average = sum / dataArray.length;
                
                // Convert to percentage
                const percentage = (average / 255) * 100;
                this.vuLevel.style.width = `${percentage}%`;
                
                // Update audio level in self-awareness monitor
                if (window.selfAwarenessUI) {
                    const dbLevel = 20 * Math.log10(average / 255) || -60;
                    window.selfAwarenessUI.updateAudioLevel(Math.max(-60, dbLevel));
                }
            }, 100); // Update every 100ms
        }
    }
    
    stopVUMeter() {
        if (this.vuMeterInterval) {
            clearInterval(this.vuMeterInterval);
            this.vuMeterInterval = null;
        }
        
        if (this.vuLevel) {
            this.vuLevel.style.width = '0%';
        }
    }
    
    handleTranscription(event) {
        const data = event.detail;
        
        if (data.error) {
            this.handleError({ message: 'Transcription error: ' + data.error });
            return;
        }
        
        this.updateTranscription(data.text || 'No speech detected', data.confidence);
        
        // Update self-awareness monitor
        if (window.selfAwarenessUI) {
            window.selfAwarenessUI.updateSTTConfidence(data.confidence || 0);
        }
    }
    
    updateTranscription(text, confidence) {
        if (this.transcriptionText) {
            this.transcriptionText.textContent = text;
        }
        
        if (this.transcriptionConfidence && confidence !== null) {
            this.transcriptionConfidence.textContent = `Confidence: ${Math.round(confidence)}%`;
            
            // Color code confidence
            if (confidence >= 80) {
                this.transcriptionConfidence.style.color = '#28a745';
            } else if (confidence >= 60) {
                this.transcriptionConfidence.style.color = '#ffc107';
            } else {
                this.transcriptionConfidence.style.color = '#dc3545';
            }
        } else if (this.transcriptionConfidence) {
            this.transcriptionConfidence.textContent = 'Confidence: --';
            this.transcriptionConfidence.style.color = '#718096';
        }
    }
    
    handleError(event) {
        const error = event.detail || event;
        console.error('Voice interface error:', error);
        
        // Reset recording state
        if (this.isRecording) {
            this.stopRecording();
        }
        
        this.updateTranscription(`Error: ${error.message}`, null);
        
        // Show error to user
        if (window.selfAwarenessUI) {
            window.selfAwarenessUI.logAlert(`Voice error: ${error.message}`, 'error');
        }
    }
    
    // Public methods for external control
    setEnabled(enabled) {
        if (this.recordButton) {
            this.recordButton.disabled = !enabled;
        }
    }
    
    reset() {
        if (this.isRecording) {
            this.stopRecording();
        }
        this.updateTranscription('Ready to listen...', null);
    }
    
    getAudioDevices() {
        return navigator.mediaDevices.enumerateDevices()
            .then(devices => devices.filter(device => device.kind === 'audioinput'))
            .catch(error => {
                console.error('Error getting audio devices:', error);
                return [];
            });
    }
    
    async switchAudioDevice(deviceId) {
        const wasRecording = this.isRecording;
        
        if (wasRecording) {
            await this.stopRecording();
        }
        
        // The device will be used on next recording start
        // MediaRecorder will use the new default device
        
        if (wasRecording) {
            await this.startRecording();
        }
    }
}

// Initialize voice interface when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.voiceInterface = new VoiceInterface();
});