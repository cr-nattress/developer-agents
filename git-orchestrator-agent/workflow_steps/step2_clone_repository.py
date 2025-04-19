import os
import sys
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, List

logger = logging.getLogger(__name__)

def clone_repository(sandbox_path: str, repo_url: str, git_config: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    """
    Step 2: Clone a repository using the GitCloneAgent.
    
    Args:
        sandbox_path (str): Path to the sandbox environment
        repo_url (str): URL of the repository to clone
        git_config (Dict[str, str]): Git configuration (user.name, user.email)
        
    Returns:
        Tuple[bool, Optional[str]]: (success, repo_path) where success is True if the clone was successful,
                                   and repo_path is the path to the cloned repository
    """
    logger.info("Step 2: Cloning repository...")
    try:
        # Use a more direct approach to import the GitCloneAgent
        # Save the original path
        path_copy = sys.path.copy()
        
        # Add the git-clone-agent directory to the Python path
        clone_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'git-clone-agent'))
        
        # Import using a direct import approach
        sys.path.insert(0, clone_agent_dir)
        logger.info(f"Added {clone_agent_dir} to Python path")
        
        # Import the core module directly
        import core.agent as clone_agent_module
        GitCloneAgent = clone_agent_module.GitCloneAgent
        
        # Clone the repository using the GitCloneAgent
        clone_agent = GitCloneAgent(working_dir=sandbox_path)
        success, repo_path = clone_agent.clone_repository(
            repo_url=repo_url,
            git_config=git_config
        )
        
        # Restore the original path
        sys.path = path_copy
        
        if success:
            logger.info(f"Repository cloned successfully to: {repo_path}")
            
            # List the contents of the cloned repository
            logger.info("Contents of the cloned repository:")
            for item in os.listdir(repo_path):
                logger.info(f"  - {item}")
                
            return True, repo_path
        else:
            logger.error(f"Failed to clone repository: {clone_agent.error_message}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error cloning repository: {str(e)}")
        return False, None

def cleanup_on_failure(sandbox_path: str) -> None:
    """
    Clean up the sandbox if the clone operation failed.
    
    Args:
        sandbox_path (str): Path to the sandbox environment
    """
    try:
        # Add the git-sandbox-agent directory to the Python path
        sandbox_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'git-sandbox-agent'))
        if sandbox_agent_dir not in sys.path:
            sys.path.insert(0, sandbox_agent_dir)
        
        # Import the sandbox_manager
        from tools import sandbox_manager
        
        # Clean up the sandbox
        sandbox_manager.cleanup_sandbox(sandbox_path)
        logger.info("Sandbox cleaned up after clone failure")
    except Exception as e:
        logger.error(f"Error cleaning up sandbox: {str(e)}")
