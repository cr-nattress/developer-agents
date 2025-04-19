import os
import logging
from pathlib import Path
from typing import List, Optional, Dict

# Import dotenv if available, otherwise provide a warning
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv package not found. Please install it with: pip install python-dotenv")

logger = logging.getLogger(__name__)

def load_env_config(required_vars: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Load environment variables from .env files.
    First loads from the central .env file in the project root,
    then loads from the agent-specific .env file which can override central values.
    
    Args:
        required_vars (List[str], optional): List of required environment variables.
            Defaults to ['GITHUB_TOKEN', 'GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL'].
    
    Returns:
        Dict[str, str]: Dictionary of loaded environment variables
    """
    if required_vars is None:
        required_vars = ['GITHUB_TOKEN', 'GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL']
    
    loaded_vars = {}
    
    if not DOTENV_AVAILABLE:
        logger.warning("Skipping .env file loading because python-dotenv is not installed.")
        return loaded_vars
    
    # Load from central .env file first
    central_env_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))
    if central_env_path.exists():
        logger.info(f"Loading environment variables from central .env file: {central_env_path}")
        load_dotenv(central_env_path)
        logger.info("Central .env file loaded successfully")
    else:
        logger.warning(f"Central .env file not found at {central_env_path}")
    
    # Then load from agent-specific .env file (which can override central values)
    agent_env_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))
    if agent_env_path.exists():
        logger.info(f"Loading environment variables from agent-specific .env file: {agent_env_path}")
        load_dotenv(agent_env_path, override=True)
        logger.info("Agent-specific .env file loaded successfully")
    else:
        logger.warning(f"Agent-specific .env file not found at {agent_env_path}")
    
    # Check for required environment variables
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Store in our return dictionary, masking sensitive values in logs
            loaded_vars[var] = value
            if var == 'GITHUB_TOKEN':
                masked_value = value[:4] + '****' if len(value) > 4 else '****'
                logger.info(f"Found {var}: {masked_value}")
            else:
                logger.info(f"Found {var}: {value}")
        else:
            logger.warning(f"Required environment variable {var} not set")
    
    return loaded_vars

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load environment variables
    env_vars = load_env_config()
    
    # Print loaded variables
    print("Loaded environment variables:")
    for var, value in env_vars.items():
        if var == 'GITHUB_TOKEN':
            masked_value = value[:4] + '****' if len(value) > 4 else '****'
            print(f"{var}: {masked_value}")
        else:
            print(f"{var}: {value}")
