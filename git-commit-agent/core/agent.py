import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple

# Use absolute imports instead of relative imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import git_ops

logger = logging.getLogger(__name__)

class GitCommitAgent:
    """
    Agent for staging, committing, and pushing Git changes.
    
    This agent handles:
    - Staging selected changes or all changes
    - Creating commits with custom messages
    - Creating and switching branches
    - Pushing changes to remote repositories
    - Providing commit hash and status information
    """
    
    def __init__(self, repo_dir: Path):
        """
        Initialize the GitCommitAgent.
        
        Args:
            repo_dir (Path): Path to the Git repository directory
        """
        self.repo_dir = repo_dir
        self.success = False
        self.error_message = None
        self.commit_hash = None
        self.branch_name = None
        
        # Validate that the directory exists and is a Git repository
        self._validate_repo()
    
    def _validate_repo(self):
        """
        Validate that the directory exists and is a Git repository.
        
        Raises:
            RuntimeError: If the directory doesn't exist or is not a Git repository
        """
        if not self.repo_dir.exists():
            raise RuntimeError(f"Repository directory {self.repo_dir} does not exist")
        
        git_dir = self.repo_dir / ".git"
        if not git_dir.exists():
            raise RuntimeError(f"Directory {self.repo_dir} is not a Git repository")
    
    def __enter__(self):
        """
        Context manager entry point.
        
        Returns:
            GitCommitAgent: The agent instance
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        """
        pass
    
    def stage_files(self, files: List[str]) -> bool:
        """
        Stage specific files for commit.
        
        Args:
            files (List[str]): List of files to stage
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            git_ops.stage_changes(files, self.repo_dir)
            self.success = True
            return True
        except RuntimeError as e:
            self.success = False
            self.error_message = str(e)
            logger.error(f"Failed to stage files: {str(e)}")
            return False
    
    def stage_all(self) -> bool:
        """
        Stage all changes in the repository.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            git_ops.stage_all(self.repo_dir)
            self.success = True
            return True
        except RuntimeError as e:
            self.success = False
            self.error_message = str(e)
            logger.error(f"Failed to stage all changes: {str(e)}")
            return False
    
    def commit(self, message: str) -> bool:
        """
        Create a commit with the staged changes.
        
        Args:
            message (str): Commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            output = git_ops.commit_changes(message, self.repo_dir)
            self.success = True
            # Extract commit hash from output if possible
            try:
                self.commit_hash = git_ops.get_commit_hash(self.repo_dir)
            except RuntimeError:
                # If we can't get the hash, it's not a critical error
                logger.warning("Could not retrieve commit hash")
            return True
        except RuntimeError as e:
            self.success = False
            self.error_message = str(e)
            logger.error(f"Failed to commit changes: {str(e)}")
            return False
    
    def commit_all(self, message: str) -> bool:
        """
        Stage all changes and create a commit.
        
        Args:
            message (str): Commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            output = git_ops.commit_all(message, self.repo_dir)
            self.success = True
            # Extract commit hash from output if possible
            try:
                self.commit_hash = git_ops.get_commit_hash(self.repo_dir)
            except RuntimeError:
                # If we can't get the hash, it's not a critical error
                logger.warning("Could not retrieve commit hash")
            return True
        except RuntimeError as e:
            self.success = False
            self.error_message = str(e)
            logger.error(f"Failed to commit all changes: {str(e)}")
            return False
    
    def create_branch(self, branch_name: str, base_branch: Optional[str] = None) -> bool:
        """
        Create a new branch and switch to it.
        
        Args:
            branch_name (str): Name of the branch to create
            base_branch (str, optional): Base branch to create from. If provided, will checkout this branch first.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            git_ops.create_branch(branch_name, self.repo_dir, base_branch)
            self.branch_name = branch_name
            self.success = True
            return True
        except RuntimeError as e:
            self.success = False
            self.error_message = str(e)
            logger.error(f"Failed to create branch {branch_name}: {str(e)}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout an existing branch.
        
        Args:
            branch_name (str): Name of the branch to checkout
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            git_ops.checkout_branch(branch_name, self.repo_dir)
            self.branch_name = branch_name
            self.success = True
            return True
        except RuntimeError as e:
            self.success = False
            self.error_message = str(e)
            logger.error(f"Failed to checkout branch {branch_name}: {str(e)}")
            return False
    
    def push(self, branch: Optional[str] = None, remote: str = "origin") -> bool:
        """
        Push changes to the remote repository.
        
        Args:
            branch (str, optional): Branch to push. If None, the current branch is used.
            remote (str, optional): Remote name. Defaults to "origin".
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current branch if not specified
            if branch is None:
                branch = git_ops.get_current_branch(self.repo_dir)
            
            self.branch_name = branch
            output = git_ops.push_branch(branch, self.repo_dir, remote)
            self.success = True
            return True
        except RuntimeError as e:
            self.success = False
            self.error_message = str(e)
            logger.error(f"Failed to push changes: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Union[bool, str, None]]:
        """
        Get the status of the last operation.
        
        Returns:
            Dict: Status information including success, commit hash, and error message if any
        """
        status = {
            "success": self.success,
            "commit_hash": self.commit_hash,
            "branch": self.branch_name,
            "error": self.error_message
        }
        return status

# Simplified function to stage, commit, and push changes
def commit_and_push(repo_dir: Path, commit_message: str, push: bool = True, 
                   branch: Optional[str] = None, create_branch: bool = False,
                   base_branch: Optional[str] = None, remote: str = "origin") -> Dict[str, Union[bool, str, None]]:
    """
    Stage all changes, commit, and optionally push to remote.
    
    Args:
        repo_dir (Path): Path to the Git repository
        commit_message (str): Commit message
        push (bool, optional): Whether to push changes. Defaults to True.
        branch (str, optional): Branch name to use. If provided with create_branch=True, will create this branch.
        create_branch (bool, optional): Whether to create a new branch. Defaults to False.
        base_branch (str, optional): Base branch to create from. Only used if create_branch is True.
        remote (str, optional): Remote name. Defaults to "origin".
        
    Returns:
        Dict: Status information including success, commit hash, and error message if any
    """
    with GitCommitAgent(repo_dir) as agent:
        # Create a new branch if requested
        if create_branch and branch:
            if not agent.create_branch(branch, base_branch):
                return agent.get_status()
        
        # Stage and commit all changes
        if not agent.commit_all(commit_message):
            return agent.get_status()
        
        # Push changes if requested
        if push:
            agent.push(branch, remote)
        
        return agent.get_status()
