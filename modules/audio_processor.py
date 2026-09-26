"""
Audio Processor Module
Handles microphone input, noise filtering, and audio preprocessing
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy import signal
import warnings

warnings.filterwarnings('ignore')

class AudioProcessor:
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        """
        Initialize audio processor
        
        Args:
            sample_rate: Audio sample rate (Hz)
            channels: Number of audio channels (1 for mono)
            chunk_size: Number of samples per chunk
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.noise_threshold = 0.02
    
    def record_audio(self, duration=5, device=None):
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            device: Audio device index (None for default)
        
        Returns:
            numpy array of audio samples
        """
        try:
            print(f"🎤 Recording for {duration} seconds...")
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                device=device,
                dtype=np.float32
            )
            sd.wait()
            print("✅ Recording complete")
            return np.squeeze(audio)
        except Exception as e:
            print(f"❌ Error recording audio: {e}")
            return None
    
    def play_audio(self, audio, device=None):
        """
        Play audio through speakers
        
        Args:
            audio: numpy array of audio samples
            device: Audio device index (None for default)
        """
        try:
            # Normalize audio to prevent clipping
            audio = audio.astype(np.float32)
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val * 0.9
            
            sd.play(audio, samplerate=self.sample_rate, device=device)
            sd.wait()
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
    
    def remove_noise(self, audio, threshold=None):
        """
        Simple noise filtering using spectral subtraction
        
        Args:
            audio: Input audio array
            threshold: Noise threshold (default: self.noise_threshold)
        
        Returns:
            Filtered audio array
        """
        if threshold is None:
            threshold = self.noise_threshold
        
        try:
            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio ** 2))
            
            # If signal is too quiet, return as is
            if rms < threshold:
                print(f"⚠️  Low signal (RMS: {rms:.4f})")
                return audio
            
            # Apply high-pass filter to reduce low-frequency noise
            sos = signal.butter(5, 80, 'hp', fs=self.sample_rate, output='sos')
            filtered = signal.sosfilt(sos, audio)
            
            # Apply noise gate
            filtered[np.abs(filtered) < threshold] = 0
            
            return filtered
        except Exception as e:
            print(f"❌ Error removing noise: {e}")
            return audio
    
    def normalize_audio(self, audio):
        """
        Normalize audio to [-1, 1] range
        
        Args:
            audio: Input audio array
        
        Returns:
            Normalized audio array
        """
        max_val = np.max(np.abs(audio))
        if max_val == 0:
            return audio
        return audio / max_val
    
    def detect_silence(self, audio, threshold=0.02, duration=0.5):
        """
        Detect if audio contains silence
        
        Args:
            audio: Input audio array
            threshold: Energy threshold
            duration: Duration threshold in seconds
        
        Returns:
            True if audio is mostly silent
        """
        try:
            rms = np.sqrt(np.mean(audio ** 2))
            silent_samples = np.sum(np.abs(audio) < threshold)
            silent_duration = silent_samples / self.sample_rate
            
            return silent_duration > duration or rms < threshold
        except:
            return False
    
    def save_audio(self, audio, filename):
        """
        Save audio to file
        
        Args:
            audio: Audio array
            filename: Output filename
        """
        try:
            sf.write(filename, audio, self.sample_rate)
            print(f"✅ Audio saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
    
    def load_audio(self, filename):
        """
        Load audio from file
        
        Args:
            filename: Input filename
        
        Returns:
            Audio array
        """
        try:
            audio, sr = sf.read(filename, dtype=np.float32)
            if sr != self.sample_rate:
                print(f"⚠️  Sample rate mismatch: {sr} vs {self.sample_rate}")
            return np.squeeze(audio)
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            return None
    
    def get_devices(self):
        """List available audio devices"""
        devices = sd.query_devices()
        print("\n📱 Available Audio Devices:")
        for i, device in enumerate(devices):
            print(f"  {i}: {device['name']} (in: {device['max_input_channels']}, out: {device['max_output_channels']})")
        return devices
    
    def set_default_device(self, device_id):
        """Set default audio device"""
        try:
            sd.default.device = device_id
            print(f"✅ Default device set to: {device_id}")
        except Exception as e:
            print(f"❌ Error setting device: {e}")
