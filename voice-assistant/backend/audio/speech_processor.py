import whisper
import tempfile
import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import base64
import wave
import array
import struct

class SpeechProcessor:
    """Handle speech-to-text and text-to-speech processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.whisper_model = None
        self.model_size = "base"  # base, small, medium, large
        self.temp_dir = Path(tempfile.gettempdir()) / "voice_assistant"
        self.temp_dir.mkdir(exist_ok=True)
        
    async def initialize(self):
        """Initialize the speech processor"""
        try:
            # Load Whisper model asynchronously
            loop = asyncio.get_event_loop()
            self.whisper_model = await loop.run_in_executor(
                None, whisper.load_model, self.model_size
            )
            self.logger.info(f"Whisper model '{self.model_size}' loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize speech processor: {e}")
            return False
    
    async def transcribe_audio(self, audio_data: bytes, 
                             audio_format: str = "wav") -> Dict[str, Any]:
        """Transcribe audio data to text using Whisper"""
        try:
            if not self.whisper_model:
                raise Exception("Whisper model not initialized")
            
            # Save audio data to temporary file
            temp_audio_file = self.temp_dir / f"temp_audio_{asyncio.current_task().get_name()}.{audio_format}"
            
            with open(temp_audio_file, 'wb') as f:
                f.write(audio_data)
            
            # Transcribe using Whisper
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.whisper_model.transcribe, str(temp_audio_file)
            )
            
            # Clean up temp file
            temp_audio_file.unlink(missing_ok=True)
            
            return {
                'text': result['text'].strip(),
                'confidence': self._calculate_confidence(result),
                'language': result.get('language', 'en'),
                'segments': result.get('segments', []),
                'duration': result.get('duration', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'language': 'unknown',
                'segments': [],
                'duration': 0,
                'error': str(e)
            }
    
    def _calculate_confidence(self, whisper_result: Dict[str, Any]) -> float:
        """Calculate confidence score from Whisper result"""
        try:
            segments = whisper_result.get('segments', [])
            if not segments:
                return 0.0
            
            # Average the no_speech_prob across segments (lower is better)
            total_confidence = 0.0
            for segment in segments:
                # Convert no_speech_prob to confidence (invert and scale)
                no_speech_prob = segment.get('no_speech_prob', 0.5)
                confidence = (1.0 - no_speech_prob) * 100
                total_confidence += confidence
            
            return total_confidence / len(segments)
            
        except Exception:
            return 50.0  # Default confidence
    
    async def synthesize_speech(self, text: str, voice: str = "Alex", 
                              rate: int = 200) -> Dict[str, Any]:
        """Synthesize speech from text using macOS TTS"""
        try:
            if not text.strip():
                raise Exception("Empty text provided")
            
            # Create temporary files
            temp_aiff_file = self.temp_dir / f"temp_tts_{hash(text)}.aiff"
            temp_wav_file = self.temp_dir / f"temp_tts_{hash(text)}.wav"
            
            # Use macOS 'say' command to generate AIFF file
            say_command = [
                'say',
                '-v', voice,
                '-r', str(rate),
                '-o', str(temp_aiff_file),
                text
            ]
            
            process = await asyncio.create_subprocess_exec(
                *say_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"TTS generation failed: {stderr.decode()}")
            
            # Convert AIFF to WAV using FFmpeg
            await self._convert_aiff_to_wav(temp_aiff_file, temp_wav_file)
            
            # Read the WAV file
            with open(temp_wav_file, 'rb') as f:
                audio_data = f.read()
            
            # Get audio info
            audio_info = self._get_audio_info(temp_wav_file)
            
            # Clean up temp files
            temp_aiff_file.unlink(missing_ok=True)
            temp_wav_file.unlink(missing_ok=True)
            
            return {
                'audio_data': audio_data,
                'audio_format': 'wav',
                'duration': audio_info.get('duration', 0),
                'sample_rate': audio_info.get('sample_rate', 44100),
                'channels': audio_info.get('channels', 1),
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error synthesizing speech: {e}")
            return {
                'audio_data': b'',
                'audio_format': 'wav',
                'duration': 0,
                'sample_rate': 0,
                'channels': 0,
                'success': False,
                'error': str(e)
            }
    
    async def _convert_aiff_to_wav(self, aiff_file: Path, wav_file: Path):
        """Convert AIFF to WAV using FFmpeg"""
        try:
            ffmpeg_command = [
                'ffmpeg',
                '-i', str(aiff_file),
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                '-y',  # Overwrite output file
                str(wav_file)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg conversion failed: {stderr.decode()}")
                
        except Exception as e:
            self.logger.error(f"Error converting AIFF to WAV: {e}")
            raise
    
    def _get_audio_info(self, wav_file: Path) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            with wave.open(str(wav_file), 'rb') as wav:
                frames = wav.getnframes()
                sample_rate = wav.getframerate()
                duration = frames / sample_rate
                channels = wav.getnchannels()
                
                return {
                    'duration': duration,
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'frames': frames
                }
        except Exception as e:
            self.logger.error(f"Error getting audio info: {e}")
            return {}
    
    async def process_audio_level(self, audio_data: bytes) -> float:
        """Calculate audio level for VU meter"""
        try:
            # Simple RMS calculation for audio level
            if len(audio_data) < 2:
                return -60.0  # Very quiet
            
            # Convert bytes to 16-bit integers
            sample_count = len(audio_data) // 2
            samples = struct.unpack(f'<{sample_count}h', audio_data[:sample_count*2])
            
            # Calculate RMS
            if samples:
                rms = (sum(sample ** 2 for sample in samples) / len(samples)) ** 0.5
                
                # Convert to dB
                if rms > 0:
                    db_level = 20 * (rms / 32767.0)  # Normalize to 16-bit range
                    return max(-60.0, min(0.0, db_level))  # Clamp between -60dB and 0dB
            
            return -60.0
                
        except Exception as e:
            self.logger.error(f"Error calculating audio level: {e}")
            return -60.0
    
    def get_available_voices(self) -> List[str]:
        """Get available macOS TTS voices"""
        try:
            result = subprocess.run(['say', '-v', '?'], 
                                  capture_output=True, text=True)
            voices = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Extract voice name (first word)
                    voice_name = line.split()[0]
                    voices.append(voice_name)
            return voices
        except Exception as e:
            self.logger.error(f"Error getting available voices: {e}")
            return ['Alex', 'Samantha', 'Victoria']  # Default voices
    
    def set_model_size(self, size: str) -> bool:
        """Set Whisper model size"""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if size in valid_sizes:
            self.model_size = size
            self.whisper_model = None  # Will reload on next transcription
            self.logger.info(f"Whisper model size set to: {size}")
            return True
        return False
    
    async def cleanup(self):
        """Clean up temporary files and resources"""
        try:
            # Clean up temp directory
            for temp_file in self.temp_dir.glob("temp_*"):
                temp_file.unlink(missing_ok=True)
            
            self.logger.info("Speech processor cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Global speech processor instance
speech_processor = SpeechProcessor()