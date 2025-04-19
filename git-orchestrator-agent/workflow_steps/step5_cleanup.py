import os
import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def cleanup_sandbox(sandbox_path: str) -> bool:
    """
    Step 5: Clean up the sandbox environment.
    
    Args:
        sandbox_path (str): Path to the sandbox environment
        
    Returns:
        bool: True if the cleanup was successful, False otherwise
    """
    logger.info("Step 5: Cleaning up sandbox...")
    try:
        # Add the git-sandbox-agent directory to the Python path
        sandbox_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'git-sandbox-agent'))
        if sandbox_agent_dir not in sys.path:
            sys.path.insert(0, sandbox_agent_dir)
        
        # Import the sandbox_manager
        from tools import sandbox_manager
        
        # Clean up the sandbox
        sandbox_manager.cleanup_sandbox(sandbox_path)
        logger.info("Sandbox cleaned up successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error cleaning up sandbox: {str(e)}")
        return False
