import logging
import sys
import os
from pathlib import Path

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the GitCloneAgent
from core.agent import GitCloneAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clone_agent_run.log")
    ]
)

def main():
    print("\n===== GIT CLONE AGENT EXAMPLE =====\n")
    
    # Example repository to clone
    repo_url = "https://github.com/cr-nattress/ai-devops-lab.git"
    
    # Step 1: Clone a repository using the agent as a context manager
    print("Step 1: Cloning repository using context manager...")
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
                    print(f"  📁 {item.name}")
                else:
                    print(f"  📄 {item.name}")
        else:
            print(f"Failed to clone repository. Error: {agent.get_status().get('error')}")
    
    # The sandbox is automatically cleaned up when the context manager exits
    print("\nThe sandbox was automatically cleaned up.")
    
    # Step 2: Clone a repository with custom configuration
    print("\nStep 2: Cloning repository with custom configuration...")
    agent = GitCloneAgent()
    
    # Set up Git configuration
    git_config = {
        "user.name": "Example User",
        "user.email": "example@example.com"
    }
    
    success, clone_dir = agent.clone_repository(
        repo_url=repo_url,
        repo_name="custom-name",  # Specify a custom name for the clone directory
        git_config=git_config
    )
    
    if success:
        print(f"Successfully cloned {repo_url} to {clone_dir}")
        
        # Get the status information
        status = agent.get_status()
        print("\nClone operation status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    else:
        print(f"Failed to clone repository. Error: {agent.get_status().get('error')}")
    
    # Manually clean up the clone directory
    print("\nManually cleaning up the clone directory...")
    from tools.sandbox_manager import cleanup_clone_directory
    cleanup_clone_directory(clone_dir)
    print("Cleanup complete.")
    
    print("\n===== GIT CLONE AGENT EXAMPLE COMPLETE =====\n")

if __name__ == "__main__":
    main()
