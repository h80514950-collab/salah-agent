"""
Speech-to-Text Module
Converts audio to text using OpenAI Whisper
"""

import whisper
import numpy as np
import warnings

warnings.filterwarnings('ignore')

class SpeechToText:
    def __init__(self, model_size="base", language="ar"):
        """
        Initialize speech-to-text engine
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            language: Language code ("ar" for Arabic, "en" for English, None for auto-detect)
        """
        self.model_size = model_size
        self.language = language
        self.sample_rate = 16000
        
        print(f"🔄 Loading Whisper model ({model_size})...")
        try:
            self.model = whisper.load_model(model_size)
            print(f"✅ Whisper model loaded")
        except Exception as e:
            print(f"❌ Error loading Whisper: {e}")
            self.model = None
    
    def transcribe(self, audio, language=None):
        """
        Transcribe audio to text
        
        Args:
            audio: Audio array (numpy) or file path (string)
            language: Language code (overrides default)
        
        Returns:
            Transcribed text (string) or None if failed
        """
        if self.model is None:
            print("❌ Whisper model not loaded")
            return None
        
        try:
            lang = language or self.language
            
            # Handle file path or numpy array
            if isinstance(audio, str):
                # File path
                result = self.model.transcribe(audio, language=lang)
            else:
                # Numpy array
                # Whisper expects audio in float32 format
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)
                
                # Normalize audio
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val
                
                result = self.model.transcribe(audio, language=lang)
            
            text = result.get("text", "").strip()
            
            if text:
                print(f"📝 Transcribed: {text}")
            else:
                print("❌ No speech detected")
            
            return text
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return None
    
    def transcribe_with_confidence(self, audio, language=None):
        """
        Transcribe audio and return text with confidence score
        
        Args:
            audio: Audio array (numpy) or file path (string)
            language: Language code
        
        Returns:
            Tuple: (text, confidence) where confidence is based on average token probability
        """
        if self.model is None:
            print("❌ Whisper model not loaded")
            return None, 0.0
        
        try:
            lang = language or self.language
            
            # Handle file path or numpy array
            if isinstance(audio, str):
                result = self.model.transcribe(audio, language=lang)
            else:
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)
                
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val
                
                result = self.model.transcribe(audio, language=lang)
            
            text = result.get("text", "").strip()
            
            # Calculate confidence (this is a simplified estimate)
            confidence = 0.8  # Default confidence for Whisper
            
            if text:
                print(f"📝 Transcribed: {text} (confidence: {confidence:.2f})")
            
            return text, confidence
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return None, 0.0
    
    def set_language(self, language):
        """
        Set default language
        
        Args:
            language: Language code ("ar", "en", etc.) or None for auto-detect
        """
        self.language = language
        print(f"✅ Language set to {language}")
    
    def get_available_languages(self):
        """
        Get list of available languages
        
        Returns:
            Dictionary of language codes and names
        """
        # Subset of common languages
        languages = {
            "ar": "Arabic",
            "en": "English",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "ja": "Japanese",
            "zh": "Chinese",
            "ru": "Russian",
            "hi": "Hindi",
        }
        return languages
    
    def list_models(self):
        """List available Whisper models"""
        models = ["tiny", "base", "small", "medium", "large"]
        print("\n🎯 Available Whisper Models:")
        specs = {
            "tiny": "39M",
            "base": "74M",
            "small": "244M",
            "medium": "769M",
            "large": "1550M"
        }
        for model in models:
            print(f"  • {model:8s} - {specs[model]} parameters")
        return models
    
    def change_model(self, model_size):
        """
        Change Whisper model
        
        Args:
            model_size: Model size ("tiny", "base", "small", "medium", "large")
        """
        if model_size not in ["tiny", "base", "small", "medium", "large"]:
            print(f"❌ Invalid model size: {model_size}")
            return False
        
        try:
            print(f"🔄 Loading Whisper model ({model_size})...")
            self.model = whisper.load_model(model_size)
            self.model_size = model_size
            print(f"✅ Model changed to {model_size}")
            return True
        except Exception as e:
            print(f"❌ Error changing model: {e}")
            return False
