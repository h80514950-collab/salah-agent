"""
Voice Recognizer Module
Speaker identification using Resemblyzer voice embeddings
"""

import numpy as np
from resemblyzer import VoiceEncoder
import warnings

warnings.filterwarnings('ignore')

class VoiceRecognizer:
    def __init__(self, similarity_threshold=0.7):
        """
        Initialize voice recognizer
        
        Args:
            similarity_threshold: Cosine similarity threshold for voice matching (0-1)
        """
        self.encoder = VoiceEncoder()
        self.similarity_threshold = similarity_threshold
        self.known_voices = {}  # {name: embedding}
    
    def register_voice(self, name, audio, sample_rate=16000):
        """
        Register a voice profile
        
        Args:
            name: User name
            audio: Audio array (numpy)
            sample_rate: Sample rate of audio
        
        Returns:
            Voice embedding (numpy array) or None if failed
        """
        try:
            # Preprocess audio: convert to float32 if needed
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Normalize audio
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val
            
            # Generate embedding
            embedding = self.encoder.embed_utterance(audio)
            self.known_voices[name] = embedding
            
            print(f"✅ Voice profile registered for '{name}'")
            return embedding
        except Exception as e:
            print(f"❌ Error registering voice: {e}")
            return None
    
    def identify_speaker(self, audio, sample_rate=16000):
        """
        Identify speaker from audio
        
        Args:
            audio: Audio array (numpy)
            sample_rate: Sample rate of audio
        
        Returns:
            Tuple: (name, similarity_score) or (None, 0.0) if no match
        """
        if not self.known_voices:
            print("⚠️  No registered voices")
            return None, 0.0
        
        try:
            # Preprocess audio
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val
            
            # Generate embedding
            test_embedding = self.encoder.embed_utterance(audio)
            
            # Compare with known voices
            best_match = None
            best_similarity = 0.0
            
            for name, known_embedding in self.known_voices.items():
                # Cosine similarity
                similarity = self._cosine_similarity(test_embedding, known_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = name
            
            # Check if similarity exceeds threshold
            if best_similarity >= self.similarity_threshold:
                print(f"✅ Identified: {best_match} (similarity: {best_similarity:.2f})")
                return best_match, best_similarity
            else:
                print(f"❌ Unknown speaker (best match: {best_similarity:.2f})")
                return None, best_similarity
        
        except Exception as e:
            print(f"❌ Error identifying speaker: {e}")
            return None, 0.0
    
    def load_voices(self, voice_embeddings_dict):
        """
        Load multiple voice profiles
        
        Args:
            voice_embeddings_dict: Dictionary {name: embedding_array}
        """
        try:
            for name, embedding in voice_embeddings_dict.items():
                # Convert to numpy array if needed
                if isinstance(embedding, list):
                    embedding = np.array(embedding)
                self.known_voices[name] = embedding
            print(f"✅ Loaded {len(self.known_voices)} voice profiles")
        except Exception as e:
            print(f"❌ Error loading voices: {e}")
    
    def clear_voices(self):
        """Clear all registered voices"""
        self.known_voices.clear()
        print("✅ All voices cleared")
    
    def set_threshold(self, threshold):
        """
        Set similarity threshold
        
        Args:
            threshold: Similarity threshold (0-1)
        """
        if 0 <= threshold <= 1:
            self.similarity_threshold = threshold
            print(f"✅ Threshold set to {threshold}")
        else:
            print("❌ Threshold must be between 0 and 1")
    
    def get_voices(self):
        """Get list of registered voices"""
        return list(self.known_voices.keys())
    
    def _cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector (numpy array)
            vec2: Second vector (numpy array)
        
        Returns:
            Similarity score (0-1)
        """
        # Normalize vectors
        vec1_norm = np.linalg.norm(vec1)
        vec2_norm = np.linalg.norm(vec2)
        
        if vec1_norm == 0 or vec2_norm == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(vec1, vec2) / (vec1_norm * vec2_norm)
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
    
    def print_similarities(self, audio, sample_rate=16000):
        """
        Print similarity scores against all known voices (for debugging)
        
        Args:
            audio: Audio array (numpy)
            sample_rate: Sample rate of audio
        """
        if not self.known_voices:
            print("⚠️  No registered voices")
            return
        
        try:
            # Preprocess audio
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val
            
            test_embedding = self.encoder.embed_utterance(audio)
            
            print("\n📊 Similarity Scores:")
            for name, known_embedding in self.known_voices.items():
                similarity = self._cosine_similarity(test_embedding, known_embedding)
                status = "✅" if similarity >= self.similarity_threshold else "❌"
                print(f"  {status} {name}: {similarity:.4f}")
        except Exception as e:
            print(f"❌ Error calculating similarities: {e}")
