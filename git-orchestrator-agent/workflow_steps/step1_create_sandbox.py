import os
import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def create_sandbox() -> Optional[str]:
    """
    Step 1: Create a sandbox environment using the sandbox_manager.
    
    Returns:
        Optional[str]: Path to the created sandbox, or None if an error occurred
    """
    logger.info("Step 1: Creating sandbox environment...")
    try:
        # Add the git-sandbox-agent directory to the Python path
        sandbox_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'git-sandbox-agent'))
        if sandbox_agent_dir not in sys.path:
            sys.path.insert(0, sandbox_agent_dir)
            logger.info(f"Added {sandbox_agent_dir} to Python path")
        
        # Import the sandbox_manager
        from tools import sandbox_manager
        
        # Create a sandbox environment directly
        sandbox_path = sandbox_manager.create_sandbox()
        logger.info(f"Sandbox created at: {sandbox_path}")
        return sandbox_path
        
    except Exception as e:
        logger.error(f"Error creating sandbox: {str(e)}")
        return None
