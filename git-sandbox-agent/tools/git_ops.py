import subprocess
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

def run_git_command(args: List[str], cwd: Path) -> str:
    """
    Runs a git command in the specified directory.
    
    Args:
        args (List[str]): List of git command arguments
        cwd (Path): Working directory to run the command in
        
    Returns:
        str: Output of the git command
        
    Raises:
        RuntimeError: If the git command fails
    """
    logger.debug(f"Running git command: git {' '.join(args)} in {cwd}")
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = f"Git command failed: {result.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    return result.stdout.strip()

def clone_repo(repo_url: str, target_dir: Path, branch: Optional[str] = None) -> str:
    """
    Clones a repository into the target directory.
    
    Args:
        repo_url (str): URL of the repository to clone
        target_dir (Path): Directory to clone the repository into
        branch (Optional[str]): Branch to checkout after cloning
        
    Returns:
        str: Output of the git clone command
    """
    clone_args = ["clone", repo_url, "."]
    if branch:
        clone_args.extend(["--branch", branch])
    return run_git_command(clone_args, cwd=target_dir)
