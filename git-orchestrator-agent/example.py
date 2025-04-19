import logging
import sys
import os
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
        logging.FileHandler("orchestrator_run.log")
    ]
)

def main():
    print("\n===== GIT ORCHESTRATOR AGENT EXAMPLE =====\n")
    
    # Example parameters that would be used in a real workflow
    repo_url = "https://github.com/cr-nattress/ai-devops-lab.git"
    branch_name = "feature/test-orchestrator"
    
    # Load environment variables using the config loader
    env_vars = load_env_config()
    
    # Display loaded environment variables (with sensitive data masked)
    print("Loaded Environment Variables:")
    for var, value in env_vars.items():
        if var == 'GITHUB_TOKEN':
            masked_value = value[:4] + '****' if value else None
            print(f"  {var}: {masked_value}")
        else:
            print(f"  {var}: {value}")
    
    # Demonstrate accessing environment variables from both central and agent-specific .env files
    print("\nAccessing Environment Variables:")
    github_token = env_vars.get('GITHUB_TOKEN')
    git_author = env_vars.get('GIT_AUTHOR_NAME')
    workflow_timeout = os.environ.get('WORKFLOW_TIMEOUT')  # From agent-specific .env
    default_repo = os.environ.get('DEFAULT_REPO_URL')  # From central .env
    
    print(f"  GitHub Token: {github_token[:4]}**** (from central .env)")
    print(f"  Git Author: {git_author} (from central .env)")
    print(f"  Workflow Timeout: {workflow_timeout} seconds (from agent-specific .env)")
    print(f"  Default Repo URL: {default_repo} (from central .env)")
    
    # Demonstrate the orchestrator's role
    print("\nOrchestrator Agent Role:")
    print("  1. Coordinates the execution of specialized Git agents")
    print("  2. Maintains state between agent calls")
    print("  3. Handles the workflow sequence and error conditions")
    print("  4. Ensures proper cleanup even if errors occur")
    
    print("\nAvailable Agents:")
    agents = [
        "git-clone-agent: Clones repositories from remote sources",
        "git-branch-agent: Creates and manages branches",
        "git-commit-agent: Handles staging, committing, and pushing code changes",
        "git-pr-agent: Automates pull request creation and management",
        "git-sandbox-agent: Manages the sandbox environment for testing"
    ]
    
    for agent in agents:
        print(f"  - {agent}")
    
    print("\n===== GIT ORCHESTRATOR AGENT EXAMPLE COMPLETE =====\n")

if __name__ == "__main__":
    main()
