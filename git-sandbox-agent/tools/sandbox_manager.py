import shutil
import os
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Root directory for all sandboxes
ROOT_SANDBOX_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'application-sandbox')))

def initialize_sandbox_root() -> None:
    """
    Initializes the root application-sandbox directory.
    If the directory doesn't exist, it creates it.
    If the directory already exists, it deletes all files and folders inside it.
    """
    if ROOT_SANDBOX_DIR.exists():
        logger.info(f"Cleaning up existing application-sandbox directory at {ROOT_SANDBOX_DIR}")
        # Remove all contents but keep the directory
        for item in ROOT_SANDBOX_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink()
        logger.info(f"Cleaned up application-sandbox directory at {ROOT_SANDBOX_DIR}")
    else:
        logger.info(f"Creating application-sandbox directory at {ROOT_SANDBOX_DIR}")
        os.makedirs(ROOT_SANDBOX_DIR, exist_ok=True)
        logger.info(f"Created application-sandbox directory at {ROOT_SANDBOX_DIR}")

def create_sandbox() -> Path:
    """
    Creates a sandbox directory within the application-sandbox directory in the root.
    
    Returns:
        Path: Path to the created sandbox directory
    """
    # Initialize the root sandbox directory
    initialize_sandbox_root()
    
    # Create a unique subdirectory for this sandbox instance
    sandbox_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
    path = ROOT_SANDBOX_DIR / f"sandbox-{sandbox_id}"
    os.makedirs(path, exist_ok=True)
    
    logger.info(f"Created sandbox at {path}")
    return path

def cleanup_sandbox(path: Path) -> None:
    """
    Cleans up a sandbox directory.
    
    Args:
        path (Path): Path to the sandbox directory to clean up
    """
    if path.exists() and path.is_relative_to(ROOT_SANDBOX_DIR):
        logger.info(f"Cleaning up sandbox at {path}")
        shutil.rmtree(path, ignore_errors=True)
    elif not path.is_relative_to(ROOT_SANDBOX_DIR):
        logger.warning(f"Attempted to clean up directory outside of sandbox root: {path}")
    else:
        logger.warning(f"Attempted to clean up non-existent sandbox at {path}")
