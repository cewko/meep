import logging
import numpy as np
import sys
from typing import Optional
from pathlib import Path
from faster_whisper import WhisperModel

from config.settings import app_settings
from config.constants import DEFAULT_SENTENCE_ENDINGS
from utils.exceptions import AudioProcessingError


class SpeechRecognizer:
    """Handles speech-to-text conversion using Whisper."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._audio_settings = app_settings.audio
        self._model: Optional[WhisperModel] = None
        self._model_dir = self._audio_settings.get_models_path()
        
    def _lazy_load_model(self) -> WhisperModel:
        """Lazy load the Whisper model to improve startup time."""
        if self._model is None:
            try:
                self._model = WhisperModel(
                    self._audio_settings.whisper_model,
                    compute_type=self._audio_settings.compute_type,
                    download_root=str(self._model_dir)
                )
                self._logger.info(f"Whisper model '{self._audio_settings.whisper_model}' loaded from {self._model_dir}")
            except Exception as e:
                raise AudioProcessingError(f"Failed to load Whisper model: {e}")
        
        return self._model
    
    def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio data to text."""
        if audio_data.size == 0:
            raise AudioProcessingError("No audio data provided")
            
        try:
            model = self._lazy_load_model()
            segments, _ = model.transcribe(audio_data, language='en')
            
            text = ''.join([segment.text for segment in segments]).strip()
            
            if not text:
                return ""
                
            formatted_text = self._format_text(text)
            self._logger.info(f"Transcribed text: '{formatted_text}'")
            return formatted_text
            
        except Exception as e:
            raise AudioProcessingError(f"Transcription failed: {e}")
    
    def _format_text(self, text: str) -> str:
        """Format transcribed text with proper capitalization and punctuation."""
        if not text:
            return text
            
        # Capitalize first letter
        formatted = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Add punctuation if missing
        if not formatted.endswith(DEFAULT_SENTENCE_ENDINGS):
            formatted += "."
            
        return formatted

