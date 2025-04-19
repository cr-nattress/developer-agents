import logging
import sys
import os
from pathlib import Path

# Use direct relative imports
from core.agent import GitSandboxAgent

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
    file_handler = logging.FileHandler('sandbox_agent_run.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)
    
    print("=" * 80)
    print("GIT SANDBOX AGENT DEMO")
    print("=" * 80)
    
    # Example 1: Using the default application-sandbox directory
    try:
        print("\n[EXAMPLE 1] Using default application-sandbox directory")
        print("-" * 60)
        
        with GitSandboxAgent() as agent:
            try:
                # Set up sandbox with a repository
                repo_url = "https://github.com/cr-nattress/ai-devops-lab.git"  # Using a real repository
                branch = "main"  # Optional: specify branch to clone
                
                print(f"Setting up sandbox with repository: {repo_url}")
                sandbox_path = agent.setup_sandbox(repo_url, branch)
                print(f"Sandbox created at: {sandbox_path}")
                
                # Run validation tasks
                print("Running validation tasks...")
                validation_results = agent.run_validation(
                    # Optional: custom test command
                    test_command=["pytest", "-xvs"],
                    
                    # Optional: custom linter command
                    linter_command=["flake8"]
                )
                
                # Generate and print report
                report = agent.generate_report()
                print("\nValidation Report:")
                print(f"Overall Success: {report['summary'].get('overall_success', False)}")
                print(f"Tests Passed: {report['summary'].get('tests_passed', False)}")
                print(f"Linter Passed: {report['summary'].get('linter_passed', False)}")
                
                print("\nDetails:")
                if 'tests' in report['details']:
                    print(f"Test Command: {report['details']['tests'].get('command', 'N/A')}")
                    if not report['details']['tests'].get('success', False):
                        print(f"Test Error: {report['details']['tests'].get('error', 'N/A')}")
                
                if 'linter' in report['details']:
                    print(f"Linter Command: {report['details']['linter'].get('command', 'N/A')}")
                    if not report['details']['linter'].get('success', False):
                        print(f"Linter Error: {report['details']['linter'].get('error', 'N/A')}")
                
                # Sandbox is automatically cleaned up when exiting the context manager
                print("\nSandbox will be automatically cleaned up")
                
            except Exception as e:
                print(f"Error in Example 1: {str(e)}")
                # Log the full exception for debugging
                logging.exception("Exception in Example 1")
    except Exception as outer_e:
        print(f"Outer Error in Example 1: {str(outer_e)}")
        logging.exception("Outer Exception in Example 1")
    
    # Example 2: Using a custom working directory
    try:
        print("\n[EXAMPLE 2] Using custom working directory")
        print("-" * 60)
        
        custom_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), 'test-sandbox')))
        
        # Clear the directory if it exists
        if custom_dir.exists():
            import shutil
            import stat
            import time
            
            def handle_readonly_files(func, path, exc_info):
                # Handle read-only files by making them writable first
                if func in (os.unlink, os.rmdir) and exc_info[1].winerror == 5:  # Access denied
                    try:
                        os.chmod(path, stat.S_IWRITE)
                        time.sleep(0.1)  # Small delay to ensure the change takes effect
                        func(path)  # Try again
                    except Exception as e:
                        print(f"Still couldn't remove {path}: {e}")
            
            print(f"Clearing existing test-sandbox directory at: {custom_dir}")
            try:
                shutil.rmtree(custom_dir, onerror=handle_readonly_files)
            except Exception as e:
                print(f"Warning: Could not fully clear directory: {e}")
                # If we can't clear it, try to work with what's there
                pass
            
        # Create fresh directory
        os.makedirs(custom_dir, exist_ok=True)
        print(f"Created test-sandbox directory at: {custom_dir}")
        
        with GitSandboxAgent(working_dir=custom_dir) as agent:
            try:
                # Set up sandbox with a repository
                repo_url = "https://github.com/cr-nattress/ai-devops-lab.git"
                
                print(f"Setting up sandbox with repository: {repo_url}")
                sandbox_path = agent.setup_sandbox(repo_url)
                print(f"Using test-sandbox at: {sandbox_path}")
                
                # Run a simple validation task
                print("Running validation tasks...")
                validation_results = agent.run_validation()
                
                # Generate and print report
                report = agent.generate_report()
                print("\nValidation Report:")
                print(f"Overall Success: {report['summary'].get('overall_success', False)}")
                
                print("\nDetails:")
                if 'tests' in report['details']:
                    print(f"Test Command: {report['details']['tests'].get('command', 'N/A')}")
                    if not report['details']['tests'].get('success', False):
                        print(f"Test Error: {report['details']['tests'].get('error', 'N/A')}")
                
                if 'linter' in report['details']:
                    print(f"Linter Command: {report['details']['linter'].get('command', 'N/A')}")
                    if not report['details']['linter'].get('success', False):
                        print(f"Linter Error: {report['details']['linter'].get('error', 'N/A')}")
                
                print("\nNote: Test-sandbox directory will not be cleaned up automatically")
                
            except Exception as e:
                print(f"Error in Example 2: {str(e)}")
                # Log the full exception for debugging
                logging.exception("Exception in Example 2")
    except Exception as outer_e:
        print(f"Outer Error in Example 2: {str(outer_e)}")
        logging.exception("Outer Exception in Example 2")

if __name__ == "__main__":
    main()
