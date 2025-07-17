import logging
import win32gui
import win32process
import psutil
from typing import Tuple, Optional
from config.constants import MINECRAFT_EXECUTABLES


class MinecraftDetector:
    """Detect if Minecraft is currently focused."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    def is_minecraft_focused(self) -> bool:
        """Check if Minecraft is currently the focused application."""
        try:
            exe_name, _ = self._get_foreground_process_info()
            
            if exe_name is None:
                return False
                
            is_focused = exe_name.lower() in MINECRAFT_EXECUTABLES
            
            if is_focused:
                self._logger.debug("Minecraft is focused")
            
            return is_focused
            
        except Exception as error:
            self._logger.error(f"Error checking Minecraft focus: {error}")
            return False
    
    def _get_foreground_process_info(self) -> Tuple[Optional[str], Optional[str]]:
        """Get information about the foreground process."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            process = psutil.Process(pid)
            exe_name = process.name()
            command_line = ' '.join(process.cmdline())
            
            return exe_name, command_line
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as error:
            self._logger.debug(f"Could not get process info: {error}")
            return None, None

