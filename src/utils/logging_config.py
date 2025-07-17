import logging
import sys
import os
from pathlib import Path


def get_minecraft_stt_log_path() -> Path:
    """Get the path to the minecraft-STT log directory"""
    appdata_roaming = os.getenv('APPDATA')
    
    if not appdata_roaming:
        # Fallback to current directory
        fallback_path = Path.cwd() / 'logs'
        fallback_path.mkdir(parents=True, exist_ok=True)
        return fallback_path
   
    minecraft_stt_dir = Path(appdata_roaming) / '.minecraft' / 'minecraft-STT'
    minecraft_stt_dir.mkdir(parents=True, exist_ok=True)

    return minecraft_stt_dir


def setup_logging(
        level: int = logging.DEBUG, 
        log_file: str = 'minecraft_stt.log',
        format_string: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        clear_on_start: bool = True
    ) -> None:
    """Set up logging configuration."""
    
    log_path = Path(get_minecraft_stt_log_path()) / log_file

    if clear_on_start and log_path.exists():
        try:
            log_path.unlink()
        except Exception as e:
            print(f"Could not clear log file: {e}")

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.FileHandler(log_path, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.getLogger('faster_whisper').setLevel(logging.WARNING)
    logging.getLogger('sounddevice').setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized - File: {log_path}")

