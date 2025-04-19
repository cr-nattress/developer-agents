import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

def run_command(command: List[str], cwd: Path) -> Tuple[int, str, str]:
    """
    Runs a command in the specified directory.
    
    Args:
        command (List[str]): Command and arguments to run
        cwd (Path): Working directory to run the command in
        
    Returns:
        Tuple[int, str, str]: Return code, stdout, and stderr
    """
    logger.debug(f"Running command: {' '.join(command)} in {cwd}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def run_tests(cwd: Path, test_command: Optional[List[str]] = None) -> Dict[str, Union[bool, str]]:
    """
    Runs tests in the repository.
    
    Args:
        cwd (Path): Working directory of the repository
        test_command (Optional[List[str]]): Custom test command to run
        
    Returns:
        Dict[str, Union[bool, str]]: Test results with success status and output
    """
    if not test_command:
        # Try to detect test framework and run appropriate command
        if (cwd / "pytest.ini").exists() or (cwd / "conftest.py").exists():
            test_command = ["pytest"]
        elif (cwd / "setup.py").exists():
            test_command = ["python", "setup.py", "test"]
        else:
            test_command = ["python", "-m", "unittest", "discover"]
    
    logger.info(f"Running tests with command: {' '.join(test_command)}")
    return_code, stdout, stderr = run_command(test_command, cwd)
    
    return {
        "success": return_code == 0,
        "output": stdout,
        "error": stderr,
        "command": ' '.join(test_command)
    }

def run_linter(cwd: Path, linter_command: Optional[List[str]] = None) -> Dict[str, Union[bool, str]]:
    """
    Runs a linter in the repository.
    
    Args:
        cwd (Path): Working directory of the repository
        linter_command (Optional[List[str]]): Custom linter command to run
        
    Returns:
        Dict[str, Union[bool, str]]: Linter results with success status and output
    """
    if not linter_command:
        # Try to detect linter configuration and run appropriate command
        if (cwd / ".flake8").exists() or (cwd / "setup.cfg").exists():
            linter_command = ["flake8"]
        elif (cwd / ".pylintrc").exists():
            linter_command = ["pylint", "."] 
        else:
            linter_command = ["flake8", "."]  # Default to flake8
    
    logger.info(f"Running linter with command: {' '.join(linter_command)}")
    return_code, stdout, stderr = run_command(linter_command, cwd)
    
    return {
        "success": return_code == 0,
        "output": stdout,
        "error": stderr,
        "command": ' '.join(linter_command)
    }

def run_custom_script(cwd: Path, script_path: str, args: Optional[List[str]] = None) -> Dict[str, Union[bool, str]]:
    """
    Runs a custom script in the repository.
    
    Args:
        cwd (Path): Working directory of the repository
        script_path (str): Path to the script to run
        args (Optional[List[str]]): Arguments to pass to the script
        
    Returns:
        Dict[str, Union[bool, str]]: Script results with success status and output
    """
    command = ["python", script_path]
    if args:
        command.extend(args)
    
    logger.info(f"Running custom script: {' '.join(command)}")
    return_code, stdout, stderr = run_command(command, cwd)
    
    return {
        "success": return_code == 0,
        "output": stdout,
        "error": stderr,
        "command": ' '.join(command)
    }
