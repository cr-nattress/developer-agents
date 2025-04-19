import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import sys
import os

# Add the parent directory to the path so we can import from tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import sandbox_manager
from tools import git_ops
from tools import validation

logger = logging.getLogger(__name__)

class GitSandboxAgent:
    """
    Agent for running validation tasks in a clean sandbox environment.
    This agent only clones repositories and runs validation tasks.
    """
    
    def __init__(self, working_dir: Optional[Path] = None):
        """
        Initialize the GitSandboxAgent.
        
        Args:
            working_dir (Optional[Path]): Custom working directory for the agent
                If provided, this will be used instead of the default application-sandbox directory
        """
        self.working_dir = working_dir
        self.sandbox_path = None
        self.validation_results = {}
    
    def setup_sandbox(self, repo_url: str, branch: Optional[str] = None) -> Path:
        """
        Set up a sandbox environment with the specified repository.
        
        Args:
            repo_url (str): URL of the repository to clone
            branch (Optional[str]): Branch to clone (if specified)
            
        Returns:
            Path: Path to the sandbox directory
        """
        # Use custom working directory if provided, otherwise create a sandbox in application-sandbox
        if self.working_dir:
            # If working_dir is provided, use it directly
            self.sandbox_path = self.working_dir
            os.makedirs(self.sandbox_path, exist_ok=True)
            logger.info(f"Using custom working directory for sandbox: {self.sandbox_path}")
        else:
            # Otherwise use the application-sandbox directory
            self.sandbox_path = sandbox_manager.create_sandbox()
            logger.info(f"Setting up sandbox for {repo_url} at {self.sandbox_path}")
        
        try:
            git_ops.clone_repo(repo_url, self.sandbox_path, branch)
            logger.info(f"Successfully cloned {repo_url} to sandbox")
            return self.sandbox_path
        except Exception as e:
            logger.error(f"Failed to set up sandbox: {str(e)}")
            self.cleanup()
            raise
    
    def run_validation(self, 
                       test_command: Optional[List[str]] = None,
                       linter_command: Optional[List[str]] = None,
                       custom_scripts: Optional[List[Dict[str, Union[str, List[str]]]]] = None) -> Dict:
        """
        Run validation tasks in the sandbox environment.
        
        Args:
            test_command (Optional[List[str]]): Custom test command to run
            linter_command (Optional[List[str]]): Custom linter command to run
            custom_scripts (Optional[List[Dict[str, Union[str, List[str]]]]]): List of custom scripts to run
            
        Returns:
            Dict: Validation results
        """
        if not self.sandbox_path:
            raise RuntimeError("Sandbox not set up. Call setup_sandbox first.")
        
        results = {}
        
        # Run tests
        try:
            results["tests"] = validation.run_tests(self.sandbox_path, test_command)
            logger.info(f"Test results: {results['tests']['success']}")
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            results["tests"] = {"success": False, "error": str(e)}
        
        # Run linter
        try:
            results["linter"] = validation.run_linter(self.sandbox_path, linter_command)
            logger.info(f"Linter results: {results['linter']['success']}")
        except Exception as e:
            logger.error(f"Error running linter: {str(e)}")
            results["linter"] = {"success": False, "error": str(e)}
        
        # Run custom scripts
        if custom_scripts:
            results["custom_scripts"] = []
            for script_config in custom_scripts:
                script_path = script_config.get("path")
                script_args = script_config.get("args", [])
                
                try:
                    script_result = validation.run_custom_script(
                        self.sandbox_path, script_path, script_args
                    )
                    results["custom_scripts"].append(script_result)
                    logger.info(f"Custom script {script_path} results: {script_result['success']}")
                except Exception as e:
                    logger.error(f"Error running custom script {script_path}: {str(e)}")
                    results["custom_scripts"].append({
                        "path": script_path,
                        "success": False,
                        "error": str(e)
                    })
        
        self.validation_results = results
        return results
    
    def generate_report(self) -> Dict:
        """
        Generate a summary report of validation results.
        
        Returns:
            Dict: Summary report
        """
        if not self.validation_results:
            return {"status": "No validation results available"}
        
        report = {
            "summary": {
                "tests_passed": self.validation_results.get("tests", {}).get("success", False),
                "linter_passed": self.validation_results.get("linter", {}).get("success", False),
            },
            "details": self.validation_results
        }
        
        # Calculate overall success
        report["summary"]["overall_success"] = (
            report["summary"]["tests_passed"] and 
            report["summary"]["linter_passed"]
        )
        
        # Add custom scripts summary if available
        custom_scripts = self.validation_results.get("custom_scripts", [])
        if custom_scripts:
            report["summary"]["custom_scripts_passed"] = all(
                script.get("success", False) for script in custom_scripts
            )
            report["summary"]["overall_success"] = (
                report["summary"]["overall_success"] and 
                report["summary"]["custom_scripts_passed"]
            )
        
        return report
    
    def cleanup(self) -> None:
        """
        Clean up the sandbox environment.
        Only cleans up sandboxes created by the agent, not custom working directories.
        """
        if self.sandbox_path and not self.working_dir:
            # Only clean up automatically created sandboxes, not custom working directories
            logger.info(f"Cleaning up sandbox at {self.sandbox_path}")
            sandbox_manager.cleanup_sandbox(self.sandbox_path)
            self.sandbox_path = None
        elif self.sandbox_path and self.working_dir:
            logger.info(f"Skipping cleanup of custom working directory: {self.sandbox_path}")
            # Just reset the path reference, don't delete the directory
            self.sandbox_path = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
