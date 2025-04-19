import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

def collect_python_files(repo_path: str, max_files: int = 5, max_total_lines: int = 2000) -> List[str]:
    """
    Recursively collect Python files from a repository path.
    
    Args:
        repo_path (str): Path to the repository
        max_files (int): Maximum number of files to collect
        max_total_lines (int): Maximum total number of lines across all files
        
    Returns:
        List[str]: List of Python file paths
    """
    logger.info(f"Collecting Python files from {repo_path} (max {max_files} files, {max_total_lines} lines)")
    
    python_files = []
    
    for root, _, files in os.walk(repo_path):
        # Skip hidden directories and __pycache__
        if '/.git/' in root.replace('\\', '/') or '/__pycache__/' in root.replace('\\', '/') or '/venv/' in root.replace('\\', '/'):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
                
                if len(python_files) >= max_files:
                    logger.info(f"Reached maximum number of files ({max_files})")
                    return python_files
    
    return python_files

def read_file_content(file_path: str) -> Tuple[str, int]:
    """
    Read the content of a file and return it along with the number of lines.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Tuple[str, int]: File content and number of lines
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            line_count = content.count('\n') + 1
            return content, line_count
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return "", 0

def bundle_code_files(repo_path: str, max_files: int = 5, max_total_lines: int = 2000) -> str:
    """
    Bundle Python files from a repository into a single string with file separators.
    
    Args:
        repo_path (str): Path to the repository
        max_files (int): Maximum number of files to include
        max_total_lines (int): Maximum total number of lines across all files
        
    Returns:
        str: Bundled code with file separators
    """
    python_files = collect_python_files(repo_path, max_files, max_total_lines)
    
    bundled_code = ""
    total_lines = 0
    included_files = 0
    
    for file_path in python_files:
        content, line_count = read_file_content(file_path)
        
        # Skip empty files
        if not content:
            continue
            
        # Check if adding this file would exceed the maximum line count
        if total_lines + line_count > max_total_lines:
            logger.info(f"Reached maximum total lines ({max_total_lines})")
            break
            
        # Add file separator and content
        relative_path = os.path.relpath(file_path, repo_path)
        bundled_code += f"\n=== FILE: {relative_path} ===\n{content}\n"
        
        total_lines += line_count
        included_files += 1
    
    logger.info(f"Bundled {included_files} files with a total of {total_lines} lines")
    return bundled_code.strip()
