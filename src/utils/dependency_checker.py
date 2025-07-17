import importlib
from utils.exceptions import DependencyError


def check_dependencies() -> None:
    """Check if all required dependencies are installed."""
    required_modules = [
        'sounddevice',
        'numpy',
        'keyboard',
        'pynput',
        'customtkinter',
        'faster_whisper',
        'win32gui',
        'win32process',
        'psutil'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_message = (
            f"Missing required modules: {', '.join(missing_modules)}\n"
            "Please install required packages:\n"
            "pip install sounddevice numpy keyboard pynput customtkinter "
            "faster-whisper pywin32 psutil"
        )
        raise DependencyError(error_message)

