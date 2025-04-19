import logging
import sys
import os
import time
from pathlib import Path

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use direct imports
from core.agent import GitCloneAgent
from tools import sandbox_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_clone_agent():
    print("\n===== TESTING GIT CLONE AGENT =====\n")
    
    # Step 1: Initialize the sandbox root
    print("Step 1: Initializing sandbox root...")
    sandbox_manager.initialize_sandbox_root()
    print(f"Sandbox root initialized at: {sandbox_manager.ROOT_SANDBOX_DIR}")
    
    # Step 2: Clone a repository
    print("\nStep 2: Cloning repository...")
    repo_url = "https://github.com/cr-nattress/ai-devops-lab.git"
    
    with GitCloneAgent() as agent:
        success, clone_dir = agent.clone_repository(
            repo_url=repo_url,
            branch="master"  # Optional: specify a branch
        )
        
        if success:
            print(f"Successfully cloned {repo_url} to {clone_dir}")
            
            # List the contents of the cloned repository
            print("\nContents of the cloned repository:")
            for item in clone_dir.iterdir():
                if item.is_dir():
                    print(f"  Directory: {item.name}")
                else:
                    print(f"  File: {item.name}")
                    
            # Verify that the README.md file exists
            readme_path = clone_dir / "README.md"
            if readme_path.exists():
                print(f"\nREADME.md exists at {readme_path}")
                print("First 5 lines of README.md:")
                with open(readme_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i < 5:
                            print(f"  {line.strip()}")
                        else:
                            break
            else:
                print(f"\nREADME.md does not exist at {readme_path}")
        else:
            print(f"Failed to clone repository. Error: {agent.get_status().get('error')}")
    
    # Step 3: Verify that the sandbox was cleaned up
    print("\nStep 3: Verifying sandbox cleanup...")
    # Give the system a moment to complete the cleanup
    time.sleep(1)
    
    # The context manager should have cleaned up the clone directory
    if not clone_dir.exists():
        print(f"Sandbox was successfully cleaned up at: {clone_dir}")
    else:
        print(f"ERROR: Sandbox still exists at: {clone_dir}")
        # Try to manually clean it up
        try:
            sandbox_manager.cleanup_clone_directory(clone_dir)
            print(f"Manually cleaned up sandbox at: {clone_dir}")
        except Exception as e:
            print(f"Failed to manually clean up: {str(e)}")
    
    print("\n===== GIT CLONE AGENT TEST COMPLETE =====\n")

if __name__ == "__main__":
    test_clone_agent()
