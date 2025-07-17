class MinecraftSTTError(Exception):
    """Base exception for all application errors."""
    pass


class DependencyError(MinecraftSTTError):
    """Raised when required dependencies are missing."""
    pass


class AudioProcessingError(MinecraftSTTError):
    """Raised when audio processing fails."""
    pass


class HotkeyError(MinecraftSTTError):
    """Raised when hotkey binding fails."""
    pass


class MessageSendError(MinecraftSTTError):
    """Raised when message sending fails."""
    pass

