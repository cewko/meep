import logging
import time
from pynput.keyboard import Key, Controller

from config.constants import MINECRAFT_CHAT_KEY, ENTER_KEY_DELAY
from utils.exceptions import MessageSendError


class KeyboardController:
    """Handles keyboard input simulation."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._controller = Controller()
    
    def send_message_to_minecraft(self, message: str, auto_send: bool = True) -> None:
        """Send a message to Minecraft chat."""
        try:
            # Open chat
            self.simulate_key_press(MINECRAFT_CHAT_KEY)
            time.sleep(ENTER_KEY_DELAY)
            
            # Type the message
            self._controller.type(message)
            
            if auto_send:
                # Send the message
                self.simulate_key_press(Key.enter)
                self._logger.info(f"Sent to Minecraft chat: '{message}'")
            else:
                # Leave message in chat for manual editing/sending
                self._logger.info(f"Typed in Minecraft chat: '{message}' (manual send)")
                
        except Exception as error:
            raise MessageSendError(f"Failed to send message to Minecraft: {error}")
    
    def simulate_key_press(self, key: str) -> None:
        """Simulate a key press."""
        try:
            self._controller.press(key)
            self._controller.release(key)
        except Exception as error:
            self._logger.error(f"Failed to simulate key press for '{key}': {error}")

