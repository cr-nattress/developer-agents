import logging
import os
import sys
import time
import errno
from pathlib import Path

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
        logging.FileHandler("sandbox_clone_example.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    print("\n===== GIT ORCHESTRATOR SANDBOX AND CLONE EXAMPLE =====\n")
    
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
    
    # Step 1: Create a unique sandbox directory for this run
    print("\nStep 1: Creating unique sandbox environment...")
    try:
        import uuid
        import datetime
        
        # Create a unique sandbox directory with timestamp and UUID
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
        sandbox_name = f"sandbox_{timestamp}_{unique_id}"
        
        # Create the unique sandbox directory inside application-sandbox
        base_sandbox_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'application-sandbox')))
        if not os.path.exists(base_sandbox_dir):
            os.makedirs(base_sandbox_dir)
            
        sandbox_path = Path(os.path.join(base_sandbox_dir, sandbox_name))
        os.makedirs(sandbox_path)
        print(f"Created new sandbox at: {sandbox_path}")
        
    except Exception as e:
        print(f"Error creating sandbox: {str(e)}")
        return
    
    # Step 2: Clone the repository using git commands directly
    print("\nStep 2: Cloning repository...")
    import subprocess
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
            
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
    
    # Step 3: Make changes to the repository
    print("\nStep 3: Making changes to the repository...")
    try:
        # Create a new file in the repository
        new_file_path = os.path.join(sandbox_path, 'hello_from_ganon.txt')
        with open(new_file_path, 'w') as f:
            f.write(f"Hello from GANON!\nThis file was created at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"Created new file: {new_file_path}")
        
        # Modify an existing file
        readme_path = os.path.join(sandbox_path, 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'a') as f:
                f.write("\n\n## Changes by GANON\n\nThis repository was modified by the Git Orchestrator Agent.\n")
            print(f"Modified file: {readme_path}")
    except Exception as e:
        print(f"Error making changes: {str(e)}")
    
    # Step 4: Commit changes
    print("\nStep 4: Committing changes...")
    try:
        # Change to the repository directory
        os.chdir(sandbox_path)
        
        # Stage the changes
        subprocess.run(["git", "add", "."], check=True)
        print("Changes staged for commit")
        
        # Commit the changes
        commit_message = "Add hello_from_ganon.txt and update README.md"
        result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Changes committed successfully: {commit_message}")
            print(result.stdout)
        else:
            print(f"Failed to commit changes: {result.stderr}")
    except Exception as e:
        print(f"Error committing changes: {str(e)}")
    
    # Step 5: Push changes (note: this will fail without proper authentication)
    print("\nStep 5: Pushing changes...\n(Note: This will likely fail without proper authentication)")
    try:
        # Attempt to push changes
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Changes pushed successfully")
            print(result.stdout)
        else:
            print("Failed to push changes (expected without proper authentication):")
            print(result.stderr)
            print("\nTo push changes in a real scenario, you would need:")
            print("1. Proper GitHub authentication")
            print("2. Write access to the repository")
            print("3. Possibly a personal access token or SSH key")
    except Exception as e:
        print(f"Error pushing changes: {str(e)}")
    
    # Step 6: Wait for 5 seconds before cleanup
    print("\nStep 6: Waiting for 5 seconds before cleanup...")
    for i in range(5, 0, -1):
        print(f"Cleaning up in {i} seconds...", end="\r")
        time.sleep(1)
    print("\nWait complete.")
    
    # Step 7: Clean up the sandbox
    print("\nStep 7: Cleaning up sandbox...")
    try:
        import shutil
        import stat
        
        def handle_remove_readonly(func, path, exc):
            """Handle read-only files and directories when removing"""
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
    
    print("\n===== GIT ORCHESTRATOR SANDBOX AND CLONE EXAMPLE COMPLETE =====\n")

if __name__ == "__main__":
    main()
