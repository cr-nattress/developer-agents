import logging
import os
import sys
import time
from pathlib import Path

# Use direct relative imports
from tools import sandbox_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_sandbox_lifecycle():
    print("\n===== TESTING SANDBOX LIFECYCLE =====\n")
    
    # Step 1: Create a sandbox
    print("Step 1: Creating sandbox...")
    sandbox_path = sandbox_manager.create_sandbox()
    print(f"Sandbox created at: {sandbox_path}")
    
    # Step 2: Verify the sandbox exists
    print("\nStep 2: Verifying sandbox exists...")
    if sandbox_path.exists():
        print(f"Sandbox exists at: {sandbox_path}")
        
        # Create a test file in the sandbox
        test_file = sandbox_path / "test_file.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file in the sandbox.")
        print(f"Created test file at: {test_file}")
    else:
        print(f"ERROR: Sandbox does not exist at: {sandbox_path}")
    
    # Step 3: List the application-sandbox directory to see all sandboxes
    print("\nStep 3: Listing all sandboxes in application-sandbox directory...")
    root_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'application-sandbox')))
    if root_dir.exists():
        print(f"Contents of {root_dir}:")
        for item in root_dir.iterdir():
            print(f"  {item.name}")
    else:
        print(f"ERROR: Root sandbox directory does not exist at: {root_dir}")
    
    # Step 4: Wait a moment before cleanup
    print("\nStep 4: Waiting 15 seconds before cleanup...")
    time.sleep(5)
    
    # Step 5: Clean up the sandbox
    print("\nStep 5: Cleaning up sandbox...")
    sandbox_manager.cleanup_sandbox(sandbox_path)
    
    # Step 6: Verify the sandbox was removed
    print("\nStep 6: Verifying sandbox was removed...")
    if not sandbox_path.exists():
        print(f"Sandbox was successfully removed from: {sandbox_path}")
    else:
        print(f"ERROR: Sandbox still exists at: {sandbox_path}")
    
    print("\n===== SANDBOX LIFECYCLE TEST COMPLETE =====\n")

if __name__ == "__main__":
    test_sandbox_lifecycle()
