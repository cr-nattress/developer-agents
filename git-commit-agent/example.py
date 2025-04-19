import logging
import os
import sys
import time
from pathlib import Path

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the config loader and GitCommitAgent
from context.config_loader import load_env_config
from core.agent import GitCommitAgent, commit_and_push

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("commit_agent_run.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    print("\n===== GIT COMMIT AGENT EXAMPLE =====\n")
    
    # Load environment variables
    env_vars = load_env_config()
    
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
        import subprocess
        import shutil
        
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
    
    # Step 2: Clone a repository
    print("\nStep 2: Cloning repository...")
    try:
        # Get repository URL from environment or use default
        repo_url = env_vars.get('DEFAULT_REPO_URL', "https://github.com/cr-nattress/ai-devops-lab.git")
        print(f"Using repository: {repo_url}")
        
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
        return
    
    # Step 3: Create a new branch
    print("\nStep 3: Creating a new branch...")
    try:
        # Initialize the GitCommitAgent
        commit_agent = GitCommitAgent(sandbox_path)
        
        # Create a new branch
        branch_name = f"feature/test-commit-agent-{unique_id}"
        if commit_agent.create_branch(branch_name, "main"):
            print(f"Successfully created and checked out branch: {branch_name}")
        else:
            print(f"Failed to create branch: {commit_agent.error_message}")
            raise RuntimeError("Failed to create branch")
    except Exception as e:
        print(f"Error creating branch: {str(e)}")
        return
    
    # Step 4: Make changes to the repository
    print("\nStep 4: Making changes to the repository...")
    try:
        # Create a new file in the repository
        new_file_path = os.path.join(sandbox_path, 'hello_from_commit_agent.txt')
        with open(new_file_path, 'w') as f:
            f.write(f"Hello from the Git Commit Agent!\nThis file was created at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"Created new file: {new_file_path}")
        
        # Modify an existing file
        readme_path = os.path.join(sandbox_path, 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'a') as f:
                f.write("\n\n## Changes by Git Commit Agent\n\nThis repository was modified by the Git Commit Agent.\n")
            print(f"Modified file: {readme_path}")
    except Exception as e:
        print(f"Error making changes: {str(e)}")
        return
    
    # Step 5: Stage and commit the changes
    print("\nStep 5: Staging and committing changes...")
    try:
        # Stage all changes
        if commit_agent.stage_all():
            print("Successfully staged all changes")
        else:
            print(f"Failed to stage changes: {commit_agent.error_message}")
            raise RuntimeError("Failed to stage changes")
        
        # Commit the changes
        commit_message = "Add hello_from_commit_agent.txt and update README.md"
        if commit_agent.commit(commit_message):
            print(f"Successfully committed changes with message: '{commit_message}'")
            print(f"Commit hash: {commit_agent.commit_hash}")
        else:
            print(f"Failed to commit changes: {commit_agent.error_message}")
            raise RuntimeError("Failed to commit changes")
    except Exception as e:
        print(f"Error committing changes: {str(e)}")
        return
    
    # Step 6: Push the changes
    print("\nStep 6: Pushing changes...\n(Note: This will likely fail without proper authentication)")
    try:
        # Push the changes
        if commit_agent.push():
            print("Successfully pushed changes to remote repository")
        else:
            print(f"Failed to push changes: {commit_agent.error_message}")
            print("\nNote: This is expected without proper authentication.")
            print("To push changes in a real scenario, you would need:")
            print("1. Proper GitHub authentication")
            print("2. Write access to the repository")
            print("3. Possibly a personal access token or SSH key")
    except Exception as e:
        print(f"Error pushing changes: {str(e)}")
    
    # Step 7: Demonstrate the simplified commit_and_push function
    print("\nStep 7: Demonstrating simplified commit_and_push function...")
    try:
        # Create another file for the second commit
        second_file_path = os.path.join(sandbox_path, 'second_commit.txt')
        with open(second_file_path, 'w') as f:
            f.write(f"This is a second commit test.\nCreated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"Created new file: {second_file_path}")
        
        # Use the simplified function to commit and push in one call
        commit_message = "Add second_commit.txt"
        result = commit_and_push(
            repo_dir=sandbox_path,
            commit_message=commit_message,
            push=True
        )
        
        if result["success"]:
            print(f"Successfully committed and pushed changes with message: '{commit_message}'")
            print(f"Commit hash: {result['commit_hash']}")
        else:
            print(f"Failed in commit_and_push: {result['error']}")
    except Exception as e:
        print(f"Error in commit_and_push: {str(e)}")
    
    # Step 8: Wait for 5 seconds before cleanup
    print("\nStep 8: Waiting for 5 seconds before cleanup...")
    for i in range(5, 0, -1):
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
                os.chmod(path, os.stat.S_IRWXU | os.stat.S_IRWXG | os.stat.S_IRWXO)
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
    
    print("\n===== GIT COMMIT AGENT EXAMPLE COMPLETE =====\n")

if __name__ == "__main__":
    main()
