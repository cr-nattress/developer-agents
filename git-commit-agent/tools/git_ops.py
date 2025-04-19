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

def stage_changes(files: list, cwd: Path):
    """
    Stage specific files for commit.
    
    Args:
        files (list): List of files to stage
        cwd (Path): Git repository directory
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the staging operation fails
    """
    logger.info(f"Staging files {files} in {cwd}")
    return run_git_command(["add"] + files, cwd=cwd)

def stage_all(cwd: Path):
    """
    Stage all changes in the repository.
    
    Args:
        cwd (Path): Git repository directory
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the staging operation fails
    """
    logger.info(f"Staging all changes in {cwd}")
    return run_git_command(["add", "."], cwd=cwd)

def commit_changes(message: str, cwd: Path):
    """
    Create a commit with the staged changes.
    
    Args:
        message (str): Commit message
        cwd (Path): Git repository directory
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the commit operation fails
    """
    logger.info(f"Committing changes in {cwd} with message: {message}")
    return run_git_command(["commit", "-m", message], cwd=cwd)

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
    stage_all(cwd)
    return commit_changes(message, cwd)

def push_branch(branch_name: str, cwd: Path, remote: str = "origin"):
    """
    Push a branch to the remote repository.
    
    Args:
        branch_name (str): Name of the branch to push
        cwd (Path): Git repository directory
        remote (str, optional): Name of the remote. Defaults to "origin".
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the push operation fails
    """
    logger.info(f"Pushing branch {branch_name} to {remote} from {cwd}")
    return run_git_command(["push", remote, branch_name], cwd=cwd)

def get_current_branch(cwd: Path):
    """
    Get the name of the current branch.
    
    Args:
        cwd (Path): Git repository directory
        
    Returns:
        str: Current branch name
        
    Raises:
        RuntimeError: If the git command fails
    """
    logger.info(f"Getting current branch in {cwd}")
    return run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)

def get_commit_hash(cwd: Path):
    """
    Get the hash of the latest commit.
    
    Args:
        cwd (Path): Git repository directory
        
    Returns:
        str: Commit hash
        
    Raises:
        RuntimeError: If the git command fails
    """
    logger.info(f"Getting latest commit hash in {cwd}")
    return run_git_command(["rev-parse", "HEAD"], cwd=cwd)

def create_branch(branch_name: str, cwd: Path, base_branch: str = None):
    """
    Create a new branch and switch to it.
    
    Args:
        branch_name (str): Name of the branch to create
        cwd (Path): Git repository directory
        base_branch (str, optional): Base branch to create from. If provided, will checkout this branch first.
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the branch creation fails
    """
    logger.info(f"Creating branch {branch_name} in {cwd}")
    
    # If a base branch is specified, check it out first
    if base_branch:
        logger.info(f"Checking out base branch {base_branch} first")
        run_git_command(["checkout", base_branch], cwd=cwd)
    
    # Create and checkout the new branch
    return run_git_command(["checkout", "-b", branch_name], cwd=cwd)

def checkout_branch(branch_name: str, cwd: Path):
    """
    Checkout an existing branch.
    
    Args:
        branch_name (str): Name of the branch to checkout
        cwd (Path): Git repository directory
        
    Returns:
        str: Command output
        
    Raises:
        RuntimeError: If the checkout operation fails
    """
    logger.info(f"Checking out branch {branch_name} in {cwd}")
    return run_git_command(["checkout", branch_name], cwd=cwd)
