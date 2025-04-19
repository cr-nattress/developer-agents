import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import sys
import os

# Add the parent directory to the path so we can import from tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import code_collector
from tools import openai_client
from tools import code_updater

logger = logging.getLogger(__name__)

class CoderAgent:
    """
    Agent for analyzing code and creating code changes based on natural language prompts.
    This agent uses OpenAI to generate code modifications.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CoderAgent.
        
        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key
        self.openai = openai_client.OpenAIClient(api_key=api_key)
        logger.info("CoderAgent initialized")
    
    def process_repo(self, repo_path: str, prompt: str, max_files: int = 5, max_total_lines: int = 2000) -> Dict[str, Any]:
        """
        Process a repository and generate code changes based on the prompt.
        
        Args:
            repo_path (str): Path to the repository
            prompt (str): Natural language prompt for code changes
            max_files (int): Maximum number of files to include
            max_total_lines (int): Maximum total number of lines across all files
            
        Returns:
            Dict[str, Any]: Results of the code changes
        """
        logger.info(f"Processing repository at {repo_path} with prompt: {prompt}")
        
        # Step 1: Collect code context
        code_bundle = code_collector.bundle_code_files(repo_path, max_files, max_total_lines)
        if not code_bundle:
            error_msg = "No Python files found in the repository"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Step 2: Prompt OpenAI
        try:
            response = self.openai.generate_code_changes(code_bundle, prompt)
            if not response:
                error_msg = "No response received from OpenAI"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error generating code changes: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Step 3: Parse and apply changes
        file_changes = code_updater.parse_file_changes(response)
        if not file_changes:
            error_msg = "No file changes found in the response"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        results = code_updater.apply_changes(repo_path, file_changes)
        summary = code_updater.generate_diff_summary(repo_path, file_changes)
        
        # Check if all changes were applied successfully
        all_success = all(result[1] for result in results)
        
        return {
            "success": all_success,
            "files_changed": len(file_changes),
            "results": results,
            "summary": summary
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a human-readable report of the code changes.
        
        Args:
            results (Dict[str, Any]): Results from process_repo
            
        Returns:
            str: Human-readable report
        """
        if not results.get("success", False):
            return f"Error: {results.get('error', 'Unknown error')}"
        
        report = "=== CODER AGENT REPORT ===\n\n"
        report += f"Files Changed: {results.get('files_changed', 0)}\n\n"
        
        if "summary" in results:
            report += results["summary"] + "\n"
        
        if "results" in results:
            report += "\n=== DETAILED RESULTS ===\n"
            for file_path, success, message in results["results"]:
                status = "✅ Success" if success else "❌ Failed"
                report += f"{file_path}: {status} - {message}\n"
        
        return report
