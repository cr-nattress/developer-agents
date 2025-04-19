import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import from the agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.agent import CoderAgent
from context.config_loader import load_env_config

class TestCoderAgent(unittest.TestCase):
    """
    Test the CoderAgent functionality with a simple test repository.
    """
    
    def setUp(self):
        # Create a temporary directory for the test repository
        self.test_repo_dir = tempfile.mkdtemp(prefix="coder_agent_test_")
        
        # Create some Python files for testing
        self.create_test_files()
        
        # Load environment variables
        env_vars = load_env_config(['OPENAI_API_KEY'])
        self.api_key = env_vars.get('OPENAI_API_KEY')
        
        # Skip tests if API key is not available
        if not self.api_key:
            self.skipTest("OPENAI_API_KEY environment variable is required for tests")
        
        # Initialize the CoderAgent
        self.agent = CoderAgent(api_key=self.api_key)
    
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_repo_dir)
    
    def create_test_files(self):
        # Create a simple Python file without type annotations
        calculator_py = os.path.join(self.test_repo_dir, "calculator.py")
        with open(calculator_py, "w") as f:
            f.write("""
# A simple calculator module

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
        
        # Create a utils directory with a helper file
        utils_dir = os.path.join(self.test_repo_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        helper_py = os.path.join(utils_dir, "helper.py")
        with open(helper_py, "w") as f:
            f.write("""
# Helper functions

def is_even(num):
    return num % 2 == 0

def is_positive(num):
    return num > 0
""")
    
    def test_add_type_annotations(self):
        """
        Test adding type annotations to functions.
        """
        prompt = "Add type annotations to all functions"
        
        # Process the repository
        results = self.agent.process_repo(self.test_repo_dir, prompt)
        
        # Check that the process was successful
        self.assertTrue(results.get("success", False), 
                       f"Failed to process repository: {results.get('error', 'Unknown error')}")
        
        # Check that files were changed
        self.assertGreater(results.get("files_changed", 0), 0, 
                          "No files were changed")
        
        # Verify that type annotations were added to calculator.py
        calculator_py = os.path.join(self.test_repo_dir, "calculator.py")
        with open(calculator_py, "r") as f:
            content = f.read()
            self.assertIn("def add(", content)
            self.assertIn(": ", content)  # Check for type annotations
    
    def test_add_docstrings(self):
        """
        Test adding docstrings to functions.
        """
        prompt = "Add docstrings to all functions"
        
        # Process the repository
        results = self.agent.process_repo(self.test_repo_dir, prompt)
        
        # Check that the process was successful
        self.assertTrue(results.get("success", False), 
                       f"Failed to process repository: {results.get('error', 'Unknown error')}")
        
        # Check that files were changed
        self.assertGreater(results.get("files_changed", 0), 0, 
                          "No files were changed")
        
        # Verify that docstrings were added to calculator.py
        calculator_py = os.path.join(self.test_repo_dir, "calculator.py")
        with open(calculator_py, "r") as f:
            content = f.read()
            self.assertIn('"""', content)  # Check for docstrings

if __name__ == "__main__":
    unittest.main()
