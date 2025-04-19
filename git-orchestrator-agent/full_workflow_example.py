import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import workflow steps
from workflow_steps import utils
from workflow_steps import step1_create_sandbox
from workflow_steps import step2_clone_repository
from workflow_steps import step3_commit_changes
from workflow_steps import step4_wait
from workflow_steps import step5_cleanup
from workflow_steps import step6_code_changes

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

def setup_workflow():
    """
    Step 1: Setup workflow configuration and metadata.
    
    Returns:
        tuple: (repo_url, git_config, metadata) containing the repository URL, Git configuration, and workflow metadata
    """
    print("Step 1: Setting up workflow...")
    
    # Load environment variables
    env_config = utils.load_env_config()
    
    # Get repository URL from environment or use default
    repo_url = env_config.get('DEFAULT_REPO_URL', 'https://github.com/cr-nattress/ai-devops-lab.git')
    print(f"Using repository: {repo_url}")
    
    # Setup Git configuration
    git_config = {
        'user.name': env_config.get('GIT_AUTHOR_NAME', 'GANON'),
        'user.email': env_config.get('GIT_AUTHOR_EMAIL', 'your.email@example.com')
    }
    print(f"Using Git config: {git_config}")
    
    # Generate workflow ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Generate a random ID (8 hexadecimal characters)
    import random
    random_id = ''.join(random.choice('0123456789abcdef') for _ in range(8))
    workflow_id = f"{timestamp}_{random_id}"
    print(f"Workflow ID: {workflow_id}")
    
    # Create metadata for the workflow
    metadata = {
        'workflow_id': workflow_id,
        'timestamp': timestamp
    }
    
    return repo_url, git_config, metadata

def create_sandbox_environment():
    """
    Step 1: Create a sandbox environment.
    
    Returns:
        str or None: Path to the created sandbox, or None if creation failed
    """
    print("\nStep 1: Creating sandbox environment...")
    sandbox_path = step1_create_sandbox.create_sandbox()
    if not sandbox_path:
        print("Failed to create sandbox. Exiting workflow.")
        return None
    print(f"Sandbox created at: {sandbox_path}")
    return sandbox_path

def clone_repository(sandbox_path, repo_url, git_config):
    """
    Step 2: Clone the repository into the sandbox.
    
    Args:
        sandbox_path (str): Path to the sandbox environment
        repo_url (str): URL of the repository to clone
        git_config (dict): Git configuration
        
    Returns:
        tuple: (success, repo_path) where success is a boolean and repo_path is the path to the cloned repository
    """
    print("\nStep 2: Cloning repository...")
    clone_success, repo_path = step2_clone_repository.clone_repository(sandbox_path, repo_url, git_config)
    if not clone_success:
        print("Failed to clone repository. Cleaning up and exiting workflow.")
        step2_clone_repository.cleanup_on_failure(sandbox_path)
        return False, None
    print(f"Repository cloned successfully to: {repo_path}")
    return True, repo_path

def commit_changes(repo_path, metadata):
    """
    Create a branch, add or modify files, and commit changes.
    
    Args:
        repo_path (str): Path to the cloned repository
        metadata (dict): Dictionary containing metadata for the commit
        
    Returns:
        Tuple[bool, Optional[str]]: (success, commit_hash) where success is True if all operations were successful,
                                   and commit_hash is the hash of the commit
    """
    # Extract metadata with defaults
    branch_name = metadata.get('branch_name', f"feature/auto-{metadata.get('workflow_id', 'unknown')}")
    commit_message = metadata.get('commit_message', "Automated commit from Git Orchestrator")
    
    # For backward compatibility, check if we need to create a sample file
    if 'file_name' in metadata and 'file_content' in metadata:
        file_name = metadata['file_name']
        file_content = metadata['file_content']
        print(f"\nCommitting changes to {file_name} on branch {branch_name}...")
        
        success, commit_hash = step3_commit_changes.commit_changes(
            repo_path, branch_name, file_name, file_content, commit_message
        )
    else:
        # For the new workflow, we're committing existing changes
        print(f"\nCommitting existing changes on branch {branch_name}...")
        
        # TODO: Update step3_commit_changes.py to handle committing existing changes
        # For now, we'll create a placeholder file to demonstrate the workflow
        file_name = "commit_info.txt"
        file_content = f"This commit contains code improvements made at {metadata.get('timestamp', 'unknown time')}\nCommit message: {commit_message}"
        
        success, commit_hash = step3_commit_changes.commit_changes(
            repo_path, branch_name, file_name, file_content, commit_message
        )
    
    if success:
        print(f"Successfully committed changes with hash: {commit_hash}")
        return True, commit_hash
    else:
        print("Failed to commit changes. Continuing with workflow.")
        return False, None

def wait_before_cleanup(seconds=15):
    """
    Step 4: Wait for a specified number of seconds before cleanup.
    
    Args:
        seconds (int): Number of seconds to wait
    """
    print(f"\nStep 4: Waiting {seconds} seconds before cleanup...")
    step4_wait.wait(seconds)

def apply_code_changes(repo_path, code_prompt):
    """
    Step 6: Apply code changes using the CoderAgent.
    
    Args:
        repo_path (str): Path to the cloned repository
        code_prompt (str): Natural language prompt describing the code changes to make
        
    Returns:
        bool: True if code changes were applied successfully, False otherwise
    """
    print("\nStep 6: Applying code changes...")
    print(f"Repository path: {repo_path}")
    print(f"Code prompt: {code_prompt}")
    
    # Check if the repository path exists
    if not os.path.exists(repo_path):
        print(f"Error: Repository path does not exist: {repo_path}")
        return False
    
    # Check if the repository contains Python files
    python_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files in the repository")
    if python_files:
        print("Example Python files:")
        for file in python_files[:3]:  # Show up to 3 examples
            print(f"  - {os.path.relpath(file, repo_path)}")
    
    # Apply code changes
    try:
        print("\nApplying code changes with CoderAgent...")
        success, results = step6_code_changes.apply_code_changes(repo_path, code_prompt)
        
        if success and results:
            print(f"\nSuccess! Applied code changes to {results.get('files_changed', 0)} files")
            
            # Show detailed results
            if "results" in results:
                print("\nModified files:")
                for file_path, success, message in results["results"]:
                    status = "✓" if success else "✗"
                    rel_path = os.path.relpath(file_path, repo_path)
                    print(f"  {status} {rel_path}: {message}")
            
            # Show summary if available
            if "summary" in results:
                print("\nSummary of changes:")
                print(results["summary"])
                
            return True
        else:
            error_msg = "Unknown error"
            if results:
                error_msg = results.get('error', 'Unknown error')
            print(f"Failed to apply code changes: {error_msg}")
            return False
    except Exception as e:
        print(f"Exception while applying code changes: {str(e)}")
        return False

def cleanup_sandbox(sandbox_path):
    """
    Step 5: Clean up the sandbox environment.
    
    Args:
        sandbox_path (str): Path to the sandbox environment
        
    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    print("\nStep 5: Cleaning up sandbox...")
    cleanup_success = step5_cleanup.cleanup_sandbox(sandbox_path)
    if cleanup_success:
        print("Sandbox cleaned up successfully.")
        return True
    else:
        print("Workflow completed with cleanup errors.")
        print("Sandbox may need manual cleanup.")
        return False

def main():
    """
    Main function to run the full Git workflow example.
    """
    print("===== GIT ORCHESTRATOR FULL WORKFLOW EXAMPLE =====")
    
    # Step 1: Setup workflow
    repo_url, git_config, metadata = setup_workflow()
    
    sandbox_path = None
    try:
        # Step 2: Create sandbox environment
        sandbox_path = create_sandbox_environment()
        if not sandbox_path:
            print("Failed to create sandbox environment. Exiting.")
            return
        
        # Step 3: Clone repository
        clone_success, repo_path = clone_repository(sandbox_path, repo_url, git_config)
        if not clone_success:
            print("Failed to clone repository. Cleaning up sandbox.")
            return
        
        # Step 4: Create a new branch using the git branch agent
        branch_name = f"feature/auto-improvements-{metadata['workflow_id']}"
        print(f"\nStep 4: Creating new branch: {branch_name}...")
        # TODO: Implement branch creation using git branch agent
        # For now, we'll use the commit_changes function which creates a branch
        branch_success = True  # Placeholder until git branch agent is implemented
        if not branch_success:
            print(f"Failed to create branch {branch_name}. Continuing with workflow.")
        
        # Step 5: Apply code changes using the coder agent
        code_prompt = "Add docstrings to all functions that don't have them and add type hints to function parameters"
        code_change_success = apply_code_changes(repo_path, code_prompt)
        if not code_change_success:
            print("Failed to apply code changes. Continuing with workflow.")
        
        # Step 6: Commit the changes and push to remote
        print("\nStep 6: Committing and pushing changes...")
        commit_message = f"Auto-improvements: Added docstrings and type hints"
        commit_success, commit_hash = commit_changes(repo_path, {
            'branch_name': branch_name,
            'commit_message': commit_message,
            'author_name': git_config.get('user.name', 'AI Agent'),
            'author_email': git_config.get('user.email', 'ai.agent@example.com')
        })
        
        if commit_success:
            print(f"Successfully committed changes with hash: {commit_hash}")
            # TODO: Implement push to remote
            print("Push to remote not yet implemented")
        else:
            print("Failed to commit changes. Continuing with workflow.")
        
        # Wait a moment before cleanup
        wait_before_cleanup(5)
        
    except Exception as e:
        print(f"An error occurred during workflow execution: {str(e)}")
    finally:
        # Step 7: Always clean up sandbox if it was created
        if sandbox_path:
            print("\nCleaning up sandbox...")
            cleanup_sandbox(sandbox_path)
    
    print("\n===== GIT ORCHESTRATOR FULL WORKFLOW EXAMPLE COMPLETE =====\n")

if __name__ == "__main__":
    main()
