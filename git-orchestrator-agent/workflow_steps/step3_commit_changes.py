import os
import sys
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Any

logger = logging.getLogger(__name__)

def commit_changes(repo_path: str, branch_name: str, file_name: str, file_content: str, commit_message: str) -> Tuple[bool, Optional[str]]:
    """
    Step 3: Create a branch, add a file, and commit changes using the GitCommitAgent.
    
    Args:
        repo_path (str): Path to the cloned repository
        branch_name (str): Name of the branch to create
        file_name (str): Name of the file to create
        file_content (str): Content of the file to create
        commit_message (str): Commit message
        
    Returns:
        Tuple[bool, Optional[str]]: (success, commit_hash) where success is True if all operations were successful,
                                   and commit_hash is the hash of the commit
    """
    logger.info("Step 3: Creating branch, adding file, and committing changes...")
    try:
        # Use a direct import approach to avoid path conflicts
        commit_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'git-commit-agent'))
        commit_agent_core_file = os.path.join(commit_agent_dir, 'core', 'agent.py')
        logger.info(f"Loading GitCommitAgent from {commit_agent_core_file}")
        
        # Use importlib to load the module directly from the file path
        import importlib.util
        spec = importlib.util.spec_from_file_location("git_commit_agent", commit_agent_core_file)
        git_commit_agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(git_commit_agent_module)
        
        # Get the GitCommitAgent class from the loaded module
        GitCommitAgent = git_commit_agent_module.GitCommitAgent
        logger.info("Successfully imported GitCommitAgent class")
        
        # Create a new instance of the GitCommitAgent
        commit_agent = GitCommitAgent(repo_path)
        
        # Restore the original path
        sys.path = path_copy
        
        # Create a new branch
        logger.info(f"Creating branch: {branch_name}")
        if not commit_agent.create_branch(branch_name, "main"):
            logger.error(f"Failed to create branch: {commit_agent.error_message}")
            return False, None
        logger.info(f"Branch '{branch_name}' created successfully")
        
        # Create a new file
        logger.info(f"Creating file: {file_name}")
        file_path = os.path.join(repo_path, file_name)
        with open(file_path, 'w') as f:
            f.write(file_content)
        logger.info(f"File created successfully")
        
        # Stage the changes
        logger.info("Staging changes...")
        if not commit_agent.stage_all():
            logger.error(f"Failed to stage changes: {commit_agent.error_message}")
            return False, None
        logger.info("Changes staged successfully")
        
        # Commit the changes
        logger.info("Committing changes...")
        if not commit_agent.commit(commit_message):
            logger.error(f"Failed to commit changes: {commit_agent.error_message}")
            return False, None
        logger.info(f"Changes committed successfully with message: '{commit_message}'")
        logger.info(f"Commit hash: {commit_agent.commit_hash}")
        
        # Push the changes
        logger.info("Pushing changes...")
        if commit_agent.push():
            logger.info("Changes pushed successfully")
        else:
            logger.warning(f"Failed to push changes: {commit_agent.error_message}")
            logger.info("Note: This is expected without proper authentication.")
            logger.info("To push changes in a real scenario, you would need:")
            logger.info("1. Proper GitHub authentication")
            logger.info("2. Write access to the repository")
            logger.info("3. Possibly a personal access token or SSH key")
        
        return True, commit_agent.commit_hash
        
    except Exception as e:
        logger.error(f"Error in commit operations: {str(e)}")
        return False, None
