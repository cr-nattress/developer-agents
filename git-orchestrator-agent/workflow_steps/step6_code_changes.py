import os
import sys
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Any
import importlib.util

logger = logging.getLogger(__name__)

def apply_code_changes(repo_path: str, prompt: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Step 6: Apply code changes using the CoderAgent.
    
    Args:
        repo_path (str): Path to the cloned repository
        prompt (str): Natural language prompt describing the code changes to make
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: (success, results) where success is True if the code changes were applied successfully,
                                             and results contains details about the changes
    """
    logger.info("Step 6: Applying code changes...")
    try:
        # Use a more direct approach to import the CoderAgent
        # Save the original path
        path_copy = sys.path.copy()
        
        # Add the coder-agent directory to the Python path
        coder_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'coder-agent'))
        
        # Import using a direct import approach
        sys.path.insert(0, coder_agent_dir)
        logger.info(f"Added {coder_agent_dir} to Python path")
        
        # First, save the original sys.path to restore it later
        original_sys_path = sys.path.copy()
        logger.info(f"Original sys.path: {original_sys_path}")
        
        # Temporarily modify sys.path to prioritize coder-agent and its tools
        # Remove any existing paths that might conflict
        for path in list(sys.path):
            if 'git-' in path or 'agent' in path:
                sys.path.remove(path)
                logger.info(f"Removed potentially conflicting path: {path}")
        
        # Add coder-agent directory as the first entry
        sys.path.insert(0, coder_agent_dir)
        # Also add the tools directory explicitly
        tools_dir = os.path.join(coder_agent_dir, 'tools')
        sys.path.insert(1, tools_dir)
        logger.info(f"Modified sys.path: {sys.path[:5]}")
        
        try:
            # Try to import the CoderAgent class and required tools
            # First verify the tools directory exists
            if not os.path.exists(tools_dir):
                logger.error(f"Tools directory not found at {tools_dir}")
                raise ImportError(f"Tools directory not found at {tools_dir}")
            
            # Import the agent directly from the file to avoid package confusion
            core_dir = os.path.join(coder_agent_dir, 'core')
            agent_file = os.path.join(core_dir, 'agent.py')
            
            if not os.path.exists(agent_file):
                logger.error(f"Agent file not found at {agent_file}")
                raise ImportError(f"Agent file not found at {agent_file}")
            
            # First, manually import the tools modules that CoderAgent needs
            # This ensures they're in sys.modules before CoderAgent tries to import them
            tools_modules = ['code_collector', 'openai_client', 'code_updater']
            for module_name in tools_modules:
                module_path = os.path.join(tools_dir, f'{module_name}.py')
                if os.path.exists(module_path):
                    logger.info(f"Pre-importing tool module: {module_name} from {module_path}")
                    spec = importlib.util.spec_from_file_location(f"tools.{module_name}", module_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[f"tools.{module_name}"] = module
                    spec.loader.exec_module(module)
                else:
                    logger.error(f"Required tool module not found: {module_path}")
                    raise ImportError(f"Required tool module not found: {module_path}")
            
            # Now import the agent using a direct approach
            # importlib.util is already imported at the top of the file
            spec = importlib.util.spec_from_file_location("coder_agent_module", agent_file)
            coder_agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(coder_agent_module)
            
            if hasattr(coder_agent_module, 'CoderAgent'):
                logger.info("CoderAgent class found in directly imported module")
                CoderAgent = coder_agent_module.CoderAgent
            else:
                logger.error("CoderAgent class not found in agent.py file")
                raise ImportError("CoderAgent class not found in agent.py file")
        except Exception as e:
            logger.error(f"Error importing CoderAgent: {str(e)}")
            # Restore original sys.path
            sys.path = original_sys_path
            logger.info("Restored original sys.path after import error")
            raise
        
        # Get the OpenAI API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable is not set")
            return False, None
        
        # Create the CoderAgent instance
        try:
            coder_agent = CoderAgent(api_key=api_key)
            logger.info("CoderAgent instance created successfully")
        except Exception as e:
            error_msg = f"Error creating CoderAgent instance: {str(e)}"
            logger.error(error_msg)
            return False, {"error": error_msg}
        
        # Check if the repository contains Python files
        python_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(python_files)} Python files in the repository")
        
        # If no Python files, create a simple Python file for demonstration
        if not python_files:
            logger.info("No Python files found, creating a sample Python file for demonstration")
            sample_file_path = os.path.join(repo_path, 'sample_code.py')
            sample_code = """
# Sample Python code for demonstration

def hello_world():
    print(\"Hello, World!\")

def add(a, b):
    return a + b

if __name__ == '__main__':
    hello_world()
    result = add(5, 7)
    print(f\"5 + 7 = {result}\")
"""
            
            try:
                with open(sample_file_path, 'w') as f:
                    f.write(sample_code)
                logger.info(f"Created sample Python file at {sample_file_path}")
                python_files.append(sample_file_path)
            except Exception as e:
                logger.error(f"Error creating sample Python file: {str(e)}")
        
        # Process the repository with the CoderAgent
        try:
            results = coder_agent.process_repo(repo_path, prompt)
            logger.info(f"CoderAgent processing results: {results}")
            return results.get('success', False), results
        except Exception as e:
            error_msg = f"Error processing repository with CoderAgent: {str(e)}"
            logger.error(error_msg)
            return False, {"error": error_msg}
            
    except Exception as e:
        logger.error(f"Error applying code changes: {str(e)}")
        return False, None
