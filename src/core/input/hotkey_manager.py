import logging
from typing import Dict, Callable, Set
from threading import Lock

import keyboard

from utils.exceptions import HotkeyError


class HotkeyManager:
    """Manages hotkey detection and callbacks."""
    
    def __init__(
            self, hotkey_mappings: Dict[str, str],
            start_callback: Callable[[str], None],
            stop_callback: Callable[[str], None]
        ):

        self._logger = logging.getLogger(__name__)
        self._validate_hotkey_mappings(hotkey_mappings)
        
        self._hotkey_mappings = hotkey_mappings
        self._start_callback = start_callback
        self._stop_callback = stop_callback
        
        self._pressed_keys: Set[str] = set()
        self._is_running = False
        self._key_lock = Lock()
        
    def _validate_hotkey_mappings(self, mappings: Dict[str, str]) -> None:
        """Validate hotkey mappings."""
        if not mappings:
            raise HotkeyError("Hotkey mappings cannot be empty")
            
        # Check for duplicate hotkeys
        hotkeys = list(mappings.keys())
        if len(hotkeys) != len(set(hotkeys)):
            raise HotkeyError("Duplicate hotkeys found in mappings")
            
        # Validate hotkey format
        for hotkey in hotkeys:
            if not hotkey or not isinstance(hotkey, str):
                raise HotkeyError(f"Invalid hotkey format: {hotkey}")
        
    def start_monitoring(self) -> None:
        """Start monitoring hotkeys."""
        try:
            self._is_running = True
            self._logger.info(f"Started hotkey monitoring for keys: {list(self._hotkey_mappings.keys())}")
        except Exception as error:
            self._is_running = False
            raise HotkeyError(f"Failed to start hotkey monitoring: {error}")
        
    def stop_monitoring(self) -> None:
        """Stop monitoring hotkeys."""
        self._is_running = False
        with self._key_lock:
            self._pressed_keys.clear()
        self._logger.info("Stopped hotkey monitoring")
    
    def check_hotkeys(self) -> None:
        """Check hotkey states and trigger callbacks."""
        if not self._is_running:
            return
            
        try:
            with self._key_lock:
                for hotkey, prefix in self._hotkey_mappings.items():
                    try:
                        if keyboard.is_pressed(hotkey):
                            if hotkey not in self._pressed_keys:
                                self._pressed_keys.add(hotkey)
                                self._start_callback(prefix)
                        else:
                            if hotkey in self._pressed_keys:
                                self._pressed_keys.remove(hotkey)
                                self._stop_callback(prefix)
                    except Exception as error:
                        self._logger.warning(f"Error checking hotkey '{hotkey}': {error}")
                        self._pressed_keys.discard(hotkey)
                        
        except Exception as error:
            self._logger.error(f"Critical hotkey monitoring error: {error}")
            raise HotkeyError(f"Hotkey monitoring failed: {error}")
    
    def update_hotkey_mappings(self, new_mappings: Dict[str, str]) -> None:
        """Update hotkey mappings."""
        self._validate_hotkey_mappings(new_mappings)
        
        with self._key_lock:
            self._hotkey_mappings = new_mappings.copy()
            self._pressed_keys.clear()
        
        self._logger.info(f"Updated hotkey mappings: {new_mappings}")

