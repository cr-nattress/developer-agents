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

def create_clone_directory(repo_name: str = None) -> Path:
    """
    Creates a directory for cloning a repository within the application-sandbox directory.
    Ensures the directory is empty before returning it.
    
    Args:
        repo_name (str, optional): Name of the repository. If not provided, a UUID will be used.
    
    Returns:
        Path: Path to the created directory
    """
    # Initialize the root sandbox directory
    initialize_sandbox_root()
    
    # Create a directory name based on the repo name or a UUID
    if repo_name:
        # Extract just the repo name from the URL if a full URL was provided
        if '/' in repo_name:
            repo_name = repo_name.split('/')[-1]
        if '.git' in repo_name:
            repo_name = repo_name.replace('.git', '')
        
        dir_name = f"repo-{repo_name}"
    else:
        # Use UUID if no repo name is provided
        dir_name = f"repo-{str(uuid.uuid4())[:8]}"
    
    # Create the directory path
    path = ROOT_SANDBOX_DIR / dir_name
    
    # If the directory exists, clean it up first
    if path.exists():
        logger.info(f"Cleaning up existing clone directory at {path}")
        shutil.rmtree(path, ignore_errors=True)
        # Ensure it's completely removed before proceeding
        if path.exists():
            logger.warning(f"Failed to remove directory {path}, retrying...")
            import time
            time.sleep(0.5)  # Give the system a moment
            shutil.rmtree(path, ignore_errors=True)
    
    # Create a fresh directory
    os.makedirs(path, exist_ok=False)  # Should fail if directory still exists
    
    logger.info(f"Created clone directory at {path}")
    return path

def cleanup_clone_directory(path: Path) -> None:
    """
    Cleans up a clone directory.
    
    Args:
        path (Path): Path to the directory to clean up
    """
    if path.exists() and path.is_relative_to(ROOT_SANDBOX_DIR):
        logger.info(f"Cleaning up clone directory at {path}")
        shutil.rmtree(path, ignore_errors=True)
    elif not path.is_relative_to(ROOT_SANDBOX_DIR):
        logger.warning(f"Attempted to clean up directory outside of sandbox root: {path}")
    else:
        logger.warning(f"Attempted to clean up non-existent directory at {path}")
