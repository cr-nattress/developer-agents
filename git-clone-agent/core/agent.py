import logging
import os
from pathlib import Path
from typing import Dict, Optional, Union, Tuple

# Use absolute imports instead of relative imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import git_ops, sandbox_manager

logger = logging.getLogger(__name__)

class GitCloneAgent:
    """
    Agent for cloning Git repositories into a sandbox environment.
    
    This agent handles:
    - Accepting repository URLs and optional branch names
    - Setting up a sandbox environment in the application-sandbox directory
    - Cloning repositories using git
    - Optionally setting up Git configuration
    - Providing status and path information
    """
    
    def __init__(self, working_dir: Optional[Path] = None):
        """
        Initialize the GitCloneAgent.
        
        Args:
            working_dir (Path, optional): Custom working directory. If not provided,
                                         the application-sandbox directory will be used.
        """
        self.working_dir = working_dir
        self.clone_dir = None
        self.repo_url = None
        self.branch = None
        self.success = False
        self.error_message = None
    
    def __enter__(self):
        """
        Context manager entry point.
        
        Returns:
            GitCloneAgent: The agent instance
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point. Cleans up the clone directory if needed.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self.clone_dir and not self.working_dir:
            # Only clean up if we created the directory (not if a custom working_dir was provided)
            sandbox_manager.cleanup_clone_directory(self.clone_dir)
            logger.info(f"Cleaned up clone directory at {self.clone_dir}")
    
    def clone_repository(self, repo_url: str, branch: Optional[str] = None, 
                       repo_name: Optional[str] = None, git_config: Optional[Dict[str, str]] = None) -> Tuple[bool, Path]:
        """
        Clone a repository into the sandbox environment.
        
        Args:
            repo_url (str): URL of the repository to clone
            branch (str, optional): Branch to checkout after cloning
            repo_name (str, optional): Name to use for the clone directory
            git_config (Dict[str, str], optional): Git configuration to set up (e.g., user.name, user.email)
        
        Returns:
            Tuple[bool, Path]: Success status and path to the cloned repository
        """
        self.repo_url = repo_url
        self.branch = branch
        
        try:
            # Determine the clone directory
            if self.working_dir:
                self.clone_dir = self.working_dir
            else:
                # Extract repo name from URL if not provided
                if not repo_name and '/' in repo_url:
                    repo_name = repo_url.split('/')[-1]
                    if repo_name.endswith('.git'):
                        repo_name = repo_name[:-4]
                
                self.clone_dir = sandbox_manager.create_clone_directory(repo_name)
            
            # Set up Git configuration if provided
            if git_config and isinstance(git_config, dict):
                for key, value in git_config.items():
                    try:
                        git_ops.run_git_command(["config", "--global", key, value], cwd=self.clone_dir.parent)
                        logger.info(f"Set Git config {key}={value}")
                    except RuntimeError as e:
                        logger.warning(f"Failed to set Git config {key}: {str(e)}")
            
            # Clone the repository
            git_ops.clone_repo(repo_url, self.clone_dir)
            logger.info(f"Successfully cloned {repo_url} to {self.clone_dir}")
            
            # Checkout the specified branch if provided
            if branch and self.clone_dir.exists():
                git_ops.run_git_command(["checkout", branch], cwd=self.clone_dir)
                logger.info(f"Checked out branch {branch}")
            
            self.success = True
            return True, self.clone_dir
            
        except Exception as e:
            self.error_message = str(e)
            logger.error(f"Failed to clone repository: {str(e)}")
            self.success = False
            return False, self.clone_dir if self.clone_dir else Path()
    
    def get_status(self) -> Dict[str, Union[bool, str, Path]]:
        """
        Get the status of the clone operation.
        
        Returns:
            Dict: Status information including success, path, and error message if any
        """
        status = {
            "success": self.success,
            "repo_url": self.repo_url,
            "branch": self.branch,
            "clone_dir": self.clone_dir
        }
        
        if self.error_message:
            status["error"] = self.error_message
        
        return status
