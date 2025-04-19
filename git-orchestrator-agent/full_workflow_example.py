import logging
import os
import sys
import time
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
        logging.FileHandler("orchestrator_full_workflow.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    print("\n===== GIT ORCHESTRATOR FULL WORKFLOW EXAMPLE =====\n")
    
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
    
    # Step 1: Create a sandbox environment using the sandbox_manager
    print("\nStep 1: Creating sandbox environment...")
    try:
        # Add the git-sandbox-agent directory to the Python path
        sandbox_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'git-sandbox-agent'))
        if sandbox_agent_dir not in sys.path:
            sys.path.insert(0, sandbox_agent_dir)
            print(f"Added {sandbox_agent_dir} to Python path")
        
        # Import the sandbox_manager
        from tools import sandbox_manager
        
        # Create a sandbox environment directly
        sandbox_path = sandbox_manager.create_sandbox()
        print(f"Sandbox created at: {sandbox_path}")
        
    except Exception as e:
        print(f"Error creating sandbox: {str(e)}")
        return
    
    # Step 2: Import and instantiate the GitCloneAgent
    print("\nStep 2: Cloning repository...")
    try:
        # Add the git-clone-agent directory to the Python path
        clone_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'git-clone-agent'))
        if clone_agent_dir not in sys.path:
            sys.path.insert(0, clone_agent_dir)
            print(f"Added {clone_agent_dir} to Python path")
            
        # Temporarily remove other agent directories from path to avoid conflicts
        path_copy = sys.path.copy()
        sys.path = [p for p in sys.path if 'git-commit-agent' not in p and 'git-sandbox-agent' not in p] + [clone_agent_dir]
        
        # Import the GitCloneAgent
        from git_clone_agent.core.agent import GitCloneAgent
        
        # Clone the repository using the GitCloneAgent
        clone_agent = GitCloneAgent(working_dir=sandbox_path)
        success, repo_path = clone_agent.clone_repository(
            repo_url=repo_url,
            git_config=git_config
        )
        
        # Restore the original path
        sys.path = path_copy
        
        if success:
            print(f"Repository cloned successfully to: {repo_path}")
            
            # List the contents of the cloned repository
            print("\nContents of the cloned repository:")
            for item in os.listdir(repo_path):
                print(f"  - {item}")
        else:
            print(f"Failed to clone repository: {clone_agent.error_message}")
            raise RuntimeError("Failed to clone repository")
            
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
        # Clean up sandbox if clone failed
        try:
            sandbox_manager.cleanup_sandbox(sandbox_path)
        except:
            pass
        return
    
    # Step 3: Import and instantiate the GitCommitAgent
    print("\nStep 3: Creating branch, adding file, and committing changes...")
    try:
        # Add the git-commit-agent directory to the Python path
        commit_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'git-commit-agent'))
        if commit_agent_dir not in sys.path:
            sys.path.insert(0, commit_agent_dir)
            print(f"Added {commit_agent_dir} to Python path")
            
        # Temporarily remove other agent directories from path to avoid conflicts
        sys.path = [p for p in sys.path if 'git-clone-agent' not in p and 'git-sandbox-agent' not in p] + [commit_agent_dir]
            
        # Import the GitCommitAgent
        from git_commit_agent.core.agent import GitCommitAgent
        
        # Create a new instance of the GitCommitAgent
        commit_agent = GitCommitAgent(repo_path)
        
        # Restore the original path
        sys.path = path_copy
        
        # Create a new branch
        print(f"\nCreating branch: {branch_name}")
        if not commit_agent.create_branch(branch_name, "main"):
            print(f"Failed to create branch: {commit_agent.error_message}")
            raise RuntimeError("Failed to create branch")
        print(f"Branch '{branch_name}' created successfully")
        
        # Create a new file
        print(f"\nCreating file: {file_name}")
        file_path = os.path.join(repo_path, file_name)
        with open(file_path, 'w') as f:
            f.write(file_content)
        print(f"File created successfully")
        
        # Stage the changes
        print("\nStaging changes...")
        if not commit_agent.stage_all():
            print(f"Failed to stage changes: {commit_agent.error_message}")
            raise RuntimeError("Failed to stage changes")
        print("Changes staged successfully")
        
        # Commit the changes
        print("\nCommitting changes...")
        if not commit_agent.commit(commit_message):
            print(f"Failed to commit changes: {commit_agent.error_message}")
            raise RuntimeError("Failed to commit changes")
        print(f"Changes committed successfully with message: '{commit_message}'")
        print(f"Commit hash: {commit_agent.commit_hash}")
        
        # Push the changes
        print("\nPushing changes...")
        if commit_agent.push():
            print("Changes pushed successfully")
        else:
            print(f"Failed to push changes: {commit_agent.error_message}")
            print("\nNote: This is expected without proper authentication.")
            print("To push changes in a real scenario, you would need:")
            print("1. Proper GitHub authentication")
            print("2. Write access to the repository")
            print("3. Possibly a personal access token or SSH key")
        
    except Exception as e:
        print(f"Error in commit operations: {str(e)}")
    
    # Step 4: Wait for 15 seconds
    print("\nStep 4: Waiting for 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Cleaning up in {i} seconds...", end="\r")
        time.sleep(1)
    print("\nWait complete.")
    
    # Step 5: Clean up the sandbox
    print("\nStep 5: Cleaning up sandbox...")
    try:
        # Clean up the sandbox using the sandbox_manager
        sandbox_manager.cleanup_sandbox(sandbox_path)
        print("Sandbox cleaned up successfully.")
    except Exception as e:
        print(f"Error cleaning up sandbox: {str(e)}")
        print("Sandbox may need manual cleanup.")
    
    print("\n===== GIT ORCHESTRATOR FULL WORKFLOW EXAMPLE COMPLETE =====\n")

if __name__ == "__main__":
    main()
