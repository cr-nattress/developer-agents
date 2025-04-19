import os
import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

def parse_file_changes(response: str) -> Dict[str, str]:
    """
    Parse the OpenAI response to extract file changes.
    
    Args:
        response (str): Response from OpenAI
        
    Returns:
        Dict[str, str]: Dictionary mapping file paths to modified content
    """
    file_changes = {}
    
    # Regular expression to match file blocks
    pattern = r"=== FILE: ([^\n]+) ===\n([\s\S]*?)(?=\n=== FILE:|$)"
    
    matches = re.finditer(pattern, response)
    
    for match in matches:
        file_path = match.group(1).strip()
        content = match.group(2).strip()
        
        if file_path and content:
            file_changes[file_path] = content
    
    logger.info(f"Parsed {len(file_changes)} file changes from response")
    return file_changes

def apply_changes(repo_path: str, file_changes: Dict[str, str]) -> List[Tuple[str, bool, str]]:
    """
    Apply the changes to the files in the repository.
    
    Args:
        repo_path (str): Path to the repository
        file_changes (Dict[str, str]): Dictionary mapping file paths to modified content
        
    Returns:
        List[Tuple[str, bool, str]]: List of tuples containing (file_path, success, message)
    """
    results = []
    
    for file_path, content in file_changes.items():
        try:
            # Construct absolute path
            abs_path = os.path.join(repo_path, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            # Write the content to the file
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Successfully updated file: {file_path}")
            results.append((file_path, True, "Success"))
            
        except Exception as e:
            error_msg = f"Error updating file {file_path}: {str(e)}"
            logger.error(error_msg)
            results.append((file_path, False, error_msg))
    
    return results

def generate_diff_summary(repo_path: str, file_changes: Dict[str, str]) -> str:
    """
    Generate a summary of the changes made to the files.
    
    Args:
        repo_path (str): Path to the repository
        file_changes (Dict[str, str]): Dictionary mapping file paths to modified content
        
    Returns:
        str: Summary of changes
    """
    summary = "\n=== CHANGES SUMMARY ===\n"
    
    for file_path in file_changes.keys():
        abs_path = os.path.join(repo_path, file_path)
        
        # Check if the file existed before
        if os.path.exists(abs_path):
            summary += f"Modified: {file_path}\n"
        else:
            summary += f"Created: {file_path}\n"
    
    return summary
