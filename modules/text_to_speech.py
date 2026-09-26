"""
Text-to-Speech Module
Converts text to speech using pyttsx3 (offline)
"""

import pyttsx3
import threading
import warnings

warnings.filterwarnings('ignore')

class TextToSpeech:
    def __init__(self, rate=150, volume=0.9, language="ar"):
        """
        Initialize text-to-speech engine
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0-1)
            language: Language code ("ar" for Arabic, "en" for English)
        """
        self.engine = pyttsx3.init()
        self.rate = rate
        self.volume = volume
        self.language = language
        self.is_speaking = False
        
        # Set rate and volume
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # Set voice based on language
        self._set_voice(language)
        
        print(f"✅ Text-to-Speech initialized (language: {language})")
    
    def _set_voice(self, language):
        """Set voice based on language"""
        try:
            voices = self.engine.getProperty('voices')
            
            if language == "ar":
                # Try to find Arabic voice
                for voice in voices:
                    if 'arabic' in voice.languages[0].lower() if voice.languages else False:
                        self.engine.setProperty('voice', voice.id)
                        return
                # Fallback to first available voice
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
            elif language == "en":
                # Try to find English voice
                for voice in voices:
                    if 'english' in voice.languages[0].lower() if voice.languages else False:
                        self.engine.setProperty('voice', voice.id)
                        return
                # Fallback to first available voice
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"⚠️  Error setting voice: {e}")
    
    def speak(self, text, blocking=True, async_mode=False):
        """
        Speak text
        
        Args:
            text: Text to speak
            blocking: Wait for speech to finish
            async_mode: Run in separate thread
        
        Returns:
            True if successful
        """
        if not text:
            return False
        
        try:
            self.is_speaking = True
            
            if async_mode:
                thread = threading.Thread(target=self._speak_threaded, args=(text,))
                thread.daemon = True
                thread.start()
            else:
                self.engine.say(text)
                if blocking:
                    self.engine.runAndWait()
                self.is_speaking = False
            
            return True
        except Exception as e:
            print(f"❌ Error speaking: {e}")
            self.is_speaking = False
            return False
    
    def _speak_threaded(self, text):
        """Speak text in a separate thread"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        finally:
            self.is_speaking = False
    
    def stop(self):
        """Stop current speech"""
        try:
            self.engine.stop()
            self.is_speaking = False
            print("🛑 Speech stopped")
        except Exception as e:
            print(f"❌ Error stopping speech: {e}")
    
    def set_rate(self, rate):
        """
        Set speech rate
        
        Args:
            rate: Words per minute (typically 50-300)
        """
        try:
            self.rate = rate
            self.engine.setProperty('rate', rate)
            print(f"✅ Speech rate set to {rate}")
        except Exception as e:
            print(f"❌ Error setting rate: {e}")
    
    def set_volume(self, volume):
        """
        Set volume
        
        Args:
            volume: Volume level (0-1)
        """
        try:
            if 0 <= volume <= 1:
                self.volume = volume
                self.engine.setProperty('volume', volume)
                print(f"✅ Volume set to {volume}")
            else:
                print("❌ Volume must be between 0 and 1")
        except Exception as e:
            print(f"❌ Error setting volume: {e}")
    
    def set_language(self, language):
        """
        Set language and voice
        
        Args:
            language: Language code ("ar" or "en")
        """
        self.language = language
        self._set_voice(language)
        print(f"✅ Language set to {language}")
    
    def get_voices(self):
        """Get available voices"""
        try:
            voices = self.engine.getProperty('voices')
            print("\n🎙️  Available Voices:")
            for i, voice in enumerate(voices):
                print(f"  {i}: {voice.name}")
                if voice.languages:
                    print(f"     Languages: {voice.languages}")
            return voices
        except Exception as e:
            print(f"❌ Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id):
        """
        Set specific voice
        
        Args:
            voice_id: Voice ID from available voices
        """
        try:
            self.engine.setProperty('voice', voice_id)
            print(f"✅ Voice set to {voice_id}")
        except Exception as e:
            print(f"❌ Error setting voice: {e}")
    
    def speak_arabic(self, text, blocking=True):
        """Speak Arabic text"""
        self.set_language("ar")
        return self.speak(text, blocking=blocking)
    
    def speak_english(self, text, blocking=True):
        """Speak English text"""
        self.set_language("en")
        return self.speak(text, blocking=blocking)
    
    def wait_until_done(self):
        """Wait until speech is finished"""
        try:
            while self.is_speaking:
                import time
                time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error waiting: {e}")
