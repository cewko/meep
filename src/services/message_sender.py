import logging
from typing import Optional

from core.input.keyboard_controller import KeyboardController
from utils.exceptions import MessageSendError


class MessageSender:
    """Handles sending messages to Minecraft."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._keyboard_controller = KeyboardController()
        self._auto_send = True
    
    def send_message(self, message: str, auto_send: Optional[bool] = None) -> None:
        if not message.strip():
            self._logger.warning("Attempted to send empty message")
            return
            
        send_mode = auto_send if auto_send is not None else self._auto_send
        
        try:
            self._keyboard_controller.send_message_to_minecraft(message, send_mode)
            
            if send_mode:
                self._logger.info(f"Message sent automatically: '{message}'")
            else:
                self._logger.info(f"Message typed for manual send: '{message}'")
                
        except Exception as e:
            raise MessageSendError(f"Failed to send message '{message}': {e}")
    
    def set_auto_send(self, auto_send: bool) -> None:
        self._auto_send = auto_send
        self._logger.info(f"Auto-send mode set to: {auto_send}")

