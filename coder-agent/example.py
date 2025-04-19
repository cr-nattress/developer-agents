import logging
import sys
import os
from pathlib import Path

# Use direct relative imports
from core.agent import CoderAgent
from context.config_loader import load_env_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    # Set up more detailed logging
    file_handler = logging.FileHandler('coder_agent_run.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)
    
    print("=" * 80)
    print("CODER AGENT DEMO")
    print("=" * 80)
    
    # Load environment variables
    env_vars = load_env_config(['OPENAI_API_KEY'])
    if 'OPENAI_API_KEY' not in env_vars:
        print("ERROR: OPENAI_API_KEY environment variable is required.")
        print("Please set it in the .env file or as an environment variable.")
        return
    
    # Example: Process a repository with a prompt
    try:
        print("\n[EXAMPLE] Processing repository with prompt")
        print("-" * 60)
        
        # Initialize the CoderAgent
        agent = CoderAgent(api_key=env_vars['OPENAI_API_KEY'])
        
        # Get repository path from command line or use default
        if len(sys.argv) > 1:
            repo_path = sys.argv[1]
        else:
            # Use the current directory as a default example
            repo_path = os.path.dirname(os.path.abspath(__file__))
        
        # Get prompt from command line or use default
        if len(sys.argv) > 2:
            prompt = sys.argv[2]
        else:
            prompt = "Add docstrings to all functions that don't have them"
        
        print(f"Repository path: {repo_path}")
        print(f"Prompt: {prompt}")
        
        # Process the repository
        results = agent.process_repo(repo_path, prompt)
        
        # Generate and print report
        report = agent.generate_report(results)
        print("\n" + report)
        
    except Exception as e:
        print(f"Error in example: {str(e)}")
        # Log the full exception for debugging
        logging.exception("Exception in example")

if __name__ == "__main__":
    main()
