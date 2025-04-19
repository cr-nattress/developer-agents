import os
import sys
import logging
import datetime
import uuid
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def generate_workflow_id() -> str:
    """
    Generate a unique workflow ID using timestamp and UUID.
    
    Returns:
        str: Unique workflow ID
    """
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    workflow_id = f"{timestamp}_{unique_id}"
    return workflow_id

def get_workflow_metadata(workflow_id: str) -> Dict[str, str]:
    """
    Generate workflow metadata based on the workflow ID.
    
    Args:
        workflow_id (str): Unique workflow ID
        
    Returns:
        Dict[str, str]: Dictionary containing workflow metadata
    """
    unique_id = workflow_id.split('_')[-1]
    
    return {
        "branch_name": f"feature/orchestrator-workflow-{unique_id}",
        "file_name": f"orchestrator_test_{unique_id}.txt",
        "file_content": f"This file was created by the Git Orchestrator Agent.\nWorkflow ID: {workflow_id}\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "commit_message": f"Add test file via orchestrator workflow {unique_id}"
    }

def load_env_config() -> Dict[str, str]:
    """
    Load environment configuration for the workflow.
    
    Returns:
        Dict[str, str]: Dictionary containing environment configuration
    """
    # Add the git-orchestrator-agent directory to the Python path
    orchestrator_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if orchestrator_dir not in sys.path:
        sys.path.insert(0, orchestrator_dir)
    
    # Import the config loader
    from context.config_loader import load_env_config as load_config
    
    # Load environment variables
    env_vars = load_config()
    
    return env_vars
