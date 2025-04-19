import logging
import os
import sys
import time
import errno
import subprocess
import shutil
import stat
from pathlib import Path
import datetime
import uuid

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the config loader
from context.config_loader import load_env_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("orchestrator_direct_workflow.log")
    ]
)

logger = logging.getLogger(__name__)

def run_git_command(args, cwd):
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

def main():
    print("\n===== GIT ORCHESTRATOR DIRECT WORKFLOW EXAMPLE =====\n")
    
    # Load environment variables
    env_vars = load_env_config()
    
    # Get the repository URL from environment or use default
    repo_url = env_vars.get('DEFAULT_REPO_URL', "https://github.com/cr-nattress/ai-devops-lab.git")
    print(f"Using repository: {repo_url}")
    
    # Get Git configuration from environment
    git_config = {
        "user.name": env_vars.get('GIT_AUTHOR_NAME', "GANON"),
        "user.email": env_vars.get('GIT_AUTHOR_EMAIL', "your.email@example.com")
    }
    print(f"Using Git config: {git_config}")
    
    # Generate a unique ID for this workflow run
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    workflow_id = f"{timestamp}_{unique_id}"
    print(f"Workflow ID: {workflow_id}")
    
    # Create branch name and file content
    branch_name = f"feature/orchestrator-workflow-{unique_id}"
    file_name = f"orchestrator_test_{unique_id}.txt"
    file_content = f"This file was created by the Git Orchestrator Agent.\nWorkflow ID: {workflow_id}\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    commit_message = f"Add test file via orchestrator workflow {unique_id}"
    
    # Step 1: Create a sandbox environment
    print("\nStep 1: Creating sandbox environment...")
    try:
        # Create a unique sandbox directory with timestamp and UUID
        sandbox_name = f"sandbox_{timestamp}_{unique_id}"
        
        # Create the unique sandbox directory inside application-sandbox
        base_sandbox_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'application-sandbox')))
        if not os.path.exists(base_sandbox_dir):
            os.makedirs(base_sandbox_dir)
            
        sandbox_path = Path(os.path.join(base_sandbox_dir, sandbox_name))
        os.makedirs(sandbox_path)
        print(f"Sandbox created at: {sandbox_path}")
        
    except Exception as e:
        print(f"Error creating sandbox: {str(e)}")
        return
    
    # Step 2: Clone the repository
    print("\nStep 2: Cloning repository...")
    try:
        # Change to the sandbox directory
        os.chdir(sandbox_path)
        
        # Set Git configuration
        for key, value in git_config.items():
            subprocess.run(["git", "config", "--global", key, value], check=True)
            print(f"Set Git config {key}={value}")
        
        # Clone the repository
        print(f"Cloning {repo_url} to {sandbox_path}...")
        result = subprocess.run(["git", "clone", repo_url, "."], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Repository cloned successfully")
            
            # List the contents of the cloned repository
            print("\nContents of the cloned repository:")
            for item in os.listdir(sandbox_path):
                print(f"  - {item}")
        else:
            print(f"Failed to clone repository: {result.stderr}")
            raise RuntimeError("Failed to clone repository")
            
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
        # Clean up sandbox if clone failed
        try:
            shutil.rmtree(sandbox_path)
            print("Cleaned up sandbox after failed clone")
        except Exception as cleanup_error:
            print(f"Error cleaning up sandbox: {str(cleanup_error)}")
        return
    
    # Step 3: Create a new branch
    print("\nStep 3: Creating a new branch...")
    try:
        # Create and checkout a new branch
        run_git_command(["checkout", "-b", branch_name], sandbox_path)
        print(f"Created and checked out branch: {branch_name}")
    except Exception as e:
        print(f"Error creating branch: {str(e)}")
        return
    
    # Step 4: Create a new file
    print("\nStep 4: Creating a new file...")
    try:
        # Create a new file in the repository
        file_path = os.path.join(sandbox_path, file_name)
        with open(file_path, 'w') as f:
            f.write(file_content)
        print(f"Created new file: {file_path}")
    except Exception as e:
        print(f"Error creating file: {str(e)}")
        return
    
    # Step 5: Stage the changes
    print("\nStep 5: Staging changes...")
    try:
        run_git_command(["add", "."], sandbox_path)
        print("Changes staged successfully")
    except Exception as e:
        print(f"Error staging changes: {str(e)}")
        return
    
    # Step 6: Commit the changes
    print("\nStep 6: Committing changes...")
    try:
        run_git_command(["commit", "-m", commit_message], sandbox_path)
        commit_hash = run_git_command(["rev-parse", "HEAD"], sandbox_path)
        print(f"Changes committed successfully with message: '{commit_message}'")
        print(f"Commit hash: {commit_hash}")
    except Exception as e:
        print(f"Error committing changes: {str(e)}")
        return
    
    # Step 7: Push the changes
    print("\nStep 7: Pushing changes...")
    try:
        run_git_command(["push", "origin", branch_name], sandbox_path)
        print("Changes pushed successfully")
    except Exception as e:
        print(f"Error pushing changes: {str(e)}")
        print("\nNote: This is expected without proper authentication.")
        print("To push changes in a real scenario, you would need:")
        print("1. Proper GitHub authentication")
        print("2. Write access to the repository")
        print("3. Possibly a personal access token or SSH key")
    
    # Step 8: Wait for 15 seconds
    print("\nStep 8: Waiting for 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Cleaning up in {i} seconds...", end="\r")
        time.sleep(1)
    print("\nWait complete.")
    
    # Step 9: Clean up the sandbox
    print("\nStep 9: Cleaning up sandbox...")
    try:
        # Clean up function to handle read-only files
        def handle_remove_readonly(func, path, exc):
            excvalue = exc[1]
            if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
                # Change the file to be readable, writable, and executable
                os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                # Retry the operation
                func(path)
            else:
                print(f"Failed to remove {path}: {excvalue}")
        
        # First try to remove the .git directory separately (common source of issues)
        git_dir = os.path.join(sandbox_path, '.git')
        if os.path.exists(git_dir):
            print(f"Removing Git directory: {git_dir}")
            try:
                # Try to force Git to release locks
                os.chdir(os.path.dirname(sandbox_path))  # Move out of the directory
                shutil.rmtree(git_dir, onerror=handle_remove_readonly)
                print("Git directory removed successfully")
            except Exception as git_err:
                print(f"Warning: Could not fully remove Git directory: {str(git_err)}")
                print("Continuing with cleanup...")
        
        # Now try to remove the entire sandbox directory
        print(f"Removing sandbox directory: {sandbox_path}")
        try:
            shutil.rmtree(sandbox_path, onerror=handle_remove_readonly)
            print("Sandbox cleaned up successfully.")
        except Exception as rm_err:
            print(f"Warning: Could not fully remove sandbox: {str(rm_err)}")
            print("Some files may remain and need manual cleanup.")
            
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        print("Sandbox may need manual cleanup.")
    
    print("\n===== GIT ORCHESTRATOR DIRECT WORKFLOW EXAMPLE COMPLETE =====\n")

if __name__ == "__main__":
    main()
