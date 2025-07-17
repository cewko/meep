import sys
import traceback
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MinecraftSTTWindow
from utils.logging_config import setup_logging
from utils.dependency_checker import check_dependencies
from utils.exceptions import DependencyError


def main() -> int:
    print("Starting Minecraft-STT..")
   
    try:
        setup_logging(clear_on_start=True)
        print("Logging setup completed")
    except Exception as error:
        print(f"Error setting up logging: {error}")
        traceback.print_exc()
        return 1
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Minecraft-STT")
    
    try:
        check_dependencies()
        logger.info("Dependencies check passed")
    except DependencyError as error:
        logger.error(f"Dependency error: {error}")
        return 1
   
    try:
        logger.info("Initializing application window")
        application = MinecraftSTTWindow()
        logger.info("Running application")
        application.run()
        logger.info("Application closed normally")
        return 0
    except Exception as error:
        logger.error(f"Error starting application: {error}")
        return 1
    finally:
        logger.info("Minecraft-STT shutting down")


if __name__ == "__main__":
    sys.exit(main())

