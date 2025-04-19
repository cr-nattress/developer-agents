import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def run_git_command(args: list, cwd: Path):
    """
    Run a git command in the specified directory.
    
    Args:
        args (list): List of git command arguments
        cwd (Path): Working directory for the command
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the git command fails
    """
    logger.info(f"Running git command: git {' '.join(args)} in {cwd}")
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = f"Git command failed: {result.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    return result.stdout.strip()

def clone_repo(repo_url: str, target_dir: Path):
    """
    Clone a git repository into the target directory.
    
    Args:
        repo_url (str): URL of the repository to clone
        target_dir (Path): Directory to clone the repository into
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the clone operation fails
    """
    # We expect target_dir to be an empty directory that already exists
    if not target_dir.exists():
        raise RuntimeError(f"Target directory {target_dir} does not exist")
    
    # Check if the directory is empty
    if any(target_dir.iterdir()):
        raise RuntimeError(f"Target directory {target_dir} is not empty")
    
    logger.info(f"Cloning repository {repo_url} into {target_dir}")
    return run_git_command(["clone", repo_url, "."], cwd=target_dir)

def create_branch(branch_name: str, cwd: Path):
    """
    Create a new branch and switch to it.
    
    Args:
        branch_name (str): Name of the branch to create
        cwd (Path): Git repository directory
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the branch creation fails
    """
    logger.info(f"Creating branch {branch_name} in {cwd}")
    return run_git_command(["checkout", "-b", branch_name], cwd=cwd)

def commit_all(message: str, cwd: Path):
    """
    Stage all changes and create a commit.
    
    Args:
        message (str): Commit message
        cwd (Path): Git repository directory
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the commit operation fails
    """
    logger.info(f"Committing all changes in {cwd} with message: {message}")
    run_git_command(["add", "."], cwd=cwd)
    return run_git_command(["commit", "-m", message], cwd=cwd)

def push_branch(branch_name: str, cwd: Path):
    """
    Push a branch to the remote repository.
    
    Args:
        branch_name (str): Name of the branch to push
        cwd (Path): Git repository directory
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the push operation fails
    """
    logger.info(f"Pushing branch {branch_name} from {cwd}")
    return run_git_command(["push", "-u", "origin", branch_name], cwd=cwd)
