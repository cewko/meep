import logging
import customtkinter as ctk
from typing import Optional


class StatusDisplay:
    """Widget for displaying application status."""
    
    def __init__(self, parent: ctk.CTkFrame, initial_text: str = "Ready to start"):
        self._logger = logging.getLogger(__name__)
        self._parent = parent
        
        self._status_label: Optional[ctk.CTkLabel] = None
        self._create_widgets(initial_text)
    
    def _create_widgets(self, initial_text: str) -> None:
        """Create the status display widgets."""
        self._status_label = ctk.CTkLabel(
            self._parent,
            text=initial_text,
            font=ctk.CTkFont(size=14)
        )
        self._status_label.pack(pady=(0, 20))
    
    def update_status(self, message: str) -> None:
        """Update the status message."""
        if self._status_label:
            self._status_label.configure(text=message)
            self._logger.debug(f"Status updated: {message}")
    
    def destroy(self) -> None:
        """Destroy the status display."""
        if self._status_label:
            self._status_label.destroy()
    
    @property
    def current_text(self) -> str:
        """Get current status text."""
        if self._status_label:
            return self._status_label.cget("text")
        return ""

