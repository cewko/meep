import logging
import threading
from typing import Callable

from core.audio.voice_recorder import VoiceRecorder
from core.audio.speech_recognizer import SpeechRecognizer
from utils.exceptions import AudioProcessingError


class AudioProcessor:
    """Coordinates audio recording and speech recognition."""
    
    def __init__(self, transcription_callback: Callable[[str], None]):
        self._logger = logging.getLogger(__name__)
        self._transcription_callback = transcription_callback
        
        self._voice_recorder = VoiceRecorder()
        self._speech_recognizer = SpeechRecognizer()
        
    def start_recording(self) -> None:
        """Start audio recording."""
        try:
            self._voice_recorder.start_recording()
            self._logger.info("Audio recording started")
        except Exception as error:
            raise AudioProcessingError(f"Failed to start recording: {error}")
    
    def stop_recording_and_process(self) -> None:
        """Stop recording and process audio in a separate thread."""
        if not self._voice_recorder.is_recording:
            self._logger.warning("No recording in progress")
            return
            
        try:
            audio_data = self._voice_recorder.stop_recording()
            processing_thread = threading.Thread(
                target=self._process_audio,
                args=(audio_data,),
                daemon=True
            )
            processing_thread.start()
            
        except AudioProcessingError as error:
            self._logger.error(f"Recording failed: {error}")
            self._transcription_callback(None)
    
    def _process_audio(self, audio_data) -> None:
        """Process audio data and call transcription callback."""
        try:
            transcribed_text = self._speech_recognizer.transcribe(audio_data)
            self._transcription_callback(transcribed_text)
            
        except AudioProcessingError as error:
            self._logger.error(f"Audio processing failed: {error}")
            self._transcription_callback(None)
    
    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._voice_recorder.is_recording
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self._voice_recorder.cleanup()

