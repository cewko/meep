import logging
import sounddevice as sd
import numpy as np
from collections import deque
from typing import Optional
from threading import Lock

from config.settings import app_settings
from utils.exceptions import AudioProcessingError


class VoiceRecorder:
    """Handles audio recording and buffering."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._audio_settings = app_settings.audio
        
        self._audio_buffer: deque = deque()
        self._stream: Optional[sd.InputStream] = None
        self._is_recording = False
        self._buffer_lock = Lock()
        
    def start_recording(self) -> None:
        """Start audio recording."""
        if self._is_recording:
            self._logger.warning("Recording already in progress")
            return
            
        try:
            self._audio_buffer.clear()
            self._is_recording = True
            
            self._stream = sd.InputStream(
                samplerate=self._audio_settings.sample_rate,
                channels=self._audio_settings.channels,
                dtype=self._audio_settings.dtype,
                callback=self._audio_callback
            )
            self._stream.start()
            self._logger.info("Recording started")
            
        except Exception as e:
            self._is_recording = False
            raise AudioProcessingError(f"Failed to start recording: {e}")
    
    def stop_recording(self) -> np.ndarray:
        """Stop audio recording and return recorded audio."""
        if not self._is_recording:
            self._logger.warning("No recording in progress")
            return np.array([])
            
        self._is_recording = False
        
        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
                
            with self._buffer_lock:
                if not self._audio_buffer:
                    raise AudioProcessingError("No audio data captured")
                    
                audio_data = np.concatenate(list(self._audio_buffer), axis=0).squeeze()
                self._audio_buffer.clear()
                
            self._logger.info("Recording stopped")
            return audio_data
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to stop recording: {e}")
    
    def _audio_callback(self, indata: np.ndarray, _frames, _time_info, _status) -> None:
        """Audio stream callback function."""
        if self._is_recording:
            with self._buffer_lock:
                self._audio_buffer.append(indata.copy())
    
    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self._is_recording:
            self.stop_recording()

