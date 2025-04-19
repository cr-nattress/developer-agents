import logging
import os
import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class GitOrchestratorAgent:
    """
    Orchestrator agent that coordinates the execution of other Git agents.
    
    This agent:
    - Maintains state for the workflow
    - Calls other agents to perform specific tasks
    - Manages the overall workflow execution
    - Does NOT directly perform Git operations or file system management
    """
    
    def __init__(self):
        """
        Initialize the GitOrchestratorAgent.
        """
        self.state = {}
        self.agents = {}
        self._load_agents()
        
    def _load_agents(self):
        """
        Dynamically load the available Git agents.
        """
        # Define the agents to load
        agent_modules = [
            ('git_clone_agent', '../../git-clone-agent/core/agent.py', 'GitCloneAgent'),
            ('git_branch_agent', '../../git-branch-agent/core/agent.py', 'GitBranchAgent'),
            ('git_commit_agent', '../../git-commit-agent/core/agent.py', 'GitCommitAgent'),
            ('git_pr_agent', '../../git-pr-agent/core/agent.py', 'GitPrAgent'),
            ('git_sandbox_agent', '../../git-sandbox-agent/core/agent.py', 'GitSandboxAgent')
        ]
        
        # Attempt to load each agent
        for agent_name, agent_path, agent_class in agent_modules:
            try:
                # Construct the absolute path to the agent module
                module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), agent_path))
                
                if os.path.exists(module_path):
                    # Add the agent's directory to the Python path temporarily
                    agent_dir = os.path.dirname(os.path.dirname(module_path))
                    if agent_dir not in sys.path:
                        sys.path.insert(0, agent_dir)
                        logger.info(f"Added {agent_dir} to Python path")
                    
                    try:
                        # Load the module dynamically
                        spec = importlib.util.spec_from_file_location(agent_name, module_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[agent_name] = module  # Register the module
                            spec.loader.exec_module(module)
                            
                            # Get the agent class
                            if hasattr(module, agent_class):
                                self.agents[agent_name] = getattr(module, agent_class)
                                logger.info(f"Loaded agent: {agent_name}")
                            else:
                                logger.warning(f"Agent class {agent_class} not found in {module_path}")
                    except Exception as e:
                        logger.warning(f"Error loading module {agent_name}: {str(e)}")
                        # If there was an error, remove the agent's directory from path
                        if agent_dir in sys.path:
                            sys.path.remove(agent_dir)
                            logger.info(f"Removed {agent_dir} from Python path due to error")
                else:
                    logger.warning(f"Agent module not found: {module_path}")
            except Exception as e:
                logger.warning(f"Failed to load agent {agent_name}: {str(e)}")
    
    def run_git_workflow(self, repo_url: str, branch_name: str, 
                         file_content: str, commit_message: str, 
                         pr_title: str, pr_description: str, 
                         github_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a complete Git workflow by orchestrating the other agents.
        
        Args:
            repo_url (str): URL of the repository to clone
            branch_name (str): Name of the branch to create
            file_content (str): Content to write to the test file
            commit_message (str): Commit message
            pr_title (str): Pull request title
            pr_description (str): Pull request description
            github_token (str, optional): GitHub API token
            
        Returns:
            Dict[str, Any]: Workflow results including status and PR URL
        """
        result = {
            "success": False,
            "steps": [],
            "error": None,
            "pr_url": None
        }
        
        sandbox_path = None
        
        try:
            # Step 1: Create a sandbox using the GitSandboxAgent
            logger.info("Step 1: Creating sandbox environment")
            if 'git_sandbox_agent' in self.agents:
                sandbox_agent = self.agents['git_sandbox_agent']()
                sandbox_path = sandbox_agent.setup_sandbox()
                result["steps"].append({"step": "create_sandbox", "success": True, "path": str(sandbox_path)})
                self.state["sandbox_path"] = sandbox_path
            else:
                error_msg = "GitSandboxAgent not available"
                logger.error(error_msg)
                result["error"] = error_msg
                return result
            
            # Step 2: Clone the repository using the GitCloneAgent
            logger.info(f"Step 2: Cloning repository {repo_url}")
            if 'git_clone_agent' in self.agents:
                clone_agent = self.agents['git_clone_agent']()
                success, clone_dir = clone_agent.clone_repository(repo_url, working_dir=sandbox_path)
                if success:
                    result["steps"].append({"step": "clone_repo", "success": True, "path": str(clone_dir)})
                    self.state["repo_dir"] = clone_dir
                else:
                    error_msg = f"Failed to clone repository: {clone_agent.get_status().get('error')}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
            else:
                error_msg = "GitCloneAgent not available"
                logger.error(error_msg)
                result["error"] = error_msg
                return result
            
            # Step 3: Create a branch using the GitBranchAgent
            logger.info(f"Step 3: Creating branch {branch_name}")
            if 'git_branch_agent' in self.agents:
                branch_agent = self.agents['git_branch_agent']()
                success, branch_info = branch_agent.create_branch(branch_name, repo_dir=self.state["repo_dir"])
                if success:
                    result["steps"].append({"step": "create_branch", "success": True, "branch": branch_name})
                    self.state["branch_name"] = branch_name
                else:
                    error_msg = f"Failed to create branch: {branch_info.get('error')}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
            else:
                error_msg = "GitBranchAgent not available"
                logger.error(error_msg)
                result["error"] = error_msg
                return result
            
            # Step 4: Create a test file and commit changes using the GitCommitAgent
            logger.info("Step 4: Creating test file and committing changes")
            if 'git_commit_agent' in self.agents:
                commit_agent = self.agents['git_commit_agent']()
                file_path = self.state["repo_dir"] / "test_file.txt"
                success, commit_info = commit_agent.commit_changes(
                    repo_dir=self.state["repo_dir"],
                    files_to_modify=[{"path": str(file_path), "content": file_content}],
                    commit_message=commit_message
                )
                if success:
                    result["steps"].append({"step": "commit_changes", "success": True, "commit": commit_info.get("commit_hash")})
                    self.state["commit_hash"] = commit_info.get("commit_hash")
                else:
                    error_msg = f"Failed to commit changes: {commit_info.get('error')}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
            else:
                error_msg = "GitCommitAgent not available"
                logger.error(error_msg)
                result["error"] = error_msg
                return result
            
            # Step 5: Push the branch and create a PR using the GitPrAgent
            logger.info("Step 5: Creating pull request")
            if 'git_pr_agent' in self.agents:
                pr_agent = self.agents['git_pr_agent']()
                success, pr_info = pr_agent.create_pull_request(
                    repo_dir=self.state["repo_dir"],
                    base_branch="main",  # Assuming main is the default branch
                    head_branch=self.state["branch_name"],
                    title=pr_title,
                    description=pr_description,
                    github_token=github_token
                )
                if success:
                    result["steps"].append({"step": "create_pr", "success": True, "pr_url": pr_info.get("html_url")})
                    result["pr_url"] = pr_info.get("html_url")
                else:
                    error_msg = f"Failed to create pull request: {pr_info.get('error')}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
            else:
                error_msg = "GitPrAgent not available"
                logger.error(error_msg)
                result["error"] = error_msg
                return result
            
            # Workflow completed successfully
            result["success"] = True
            logger.info("Git workflow completed successfully")
            
        except Exception as e:
            error_msg = f"Workflow error: {str(e)}"
            logger.error(error_msg)
            result["error"] = error_msg
        finally:
            # Clean up the sandbox if it was created
            if sandbox_path and 'git_sandbox_agent' in self.agents:
                try:
                    logger.info(f"Cleaning up sandbox at {sandbox_path}")
                    sandbox_agent.cleanup_sandbox()
                    result["steps"].append({"step": "cleanup_sandbox", "success": True})
                except Exception as e:
                    logger.warning(f"Failed to clean up sandbox: {str(e)}")
                    result["steps"].append({"step": "cleanup_sandbox", "success": False, "error": str(e)})
        
        return result

# Simplified function to run the workflow
def run_git_workflow(repo_url: str, branch_name: str, file_content: str, 
                    commit_message: str, pr_title: str, pr_description: str, 
                    github_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a complete Git workflow by orchestrating the other agents.
    
    This is a simplified function that creates an orchestrator agent and runs the workflow.
    
    Args:
        repo_url (str): URL of the repository to clone
        branch_name (str): Name of the branch to create
        file_content (str): Content to write to the test file
        commit_message (str): Commit message
        pr_title (str): Pull request title
        pr_description (str): Pull request description
        github_token (str, optional): GitHub API token
        
    Returns:
        Dict[str, Any]: Workflow results including status and PR URL
    """
    orchestrator = GitOrchestratorAgent()
    return orchestrator.run_git_workflow(
        repo_url=repo_url,
        branch_name=branch_name,
        file_content=file_content,
        commit_message=commit_message,
        pr_title=pr_title,
        pr_description=pr_description,
        github_token=github_token
    )
