# Git Sandbox Agent

A Python agent for running validation tasks in a clean sandbox environment. This agent focuses specifically on cloning repositories and running validation tasks without modifying the repository contents. All sandbox operations take place in the `application-sandbox` directory in the root by default.

## Features

- Create isolated sandbox environments for testing
- Clone Git repositories into the sandbox
- Run tests, linters, and custom validation scripts
- Generate validation reports
- Automatic cleanup of sandbox environments

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/git-sandbox-agent.git
cd git-sandbox-agent

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from git_sandbox_agent.core.agent import GitSandboxAgent

# Use the agent as a context manager for automatic cleanup
# This will use the application-sandbox directory in the root
with GitSandboxAgent() as agent:
    # Set up sandbox with a repository
    sandbox_path = agent.setup_sandbox(
        repo_url="https://github.com/example/repo.git",
        branch="main"  # Optional
    )
    
    # Run validation tasks
    validation_results = agent.run_validation()
    
    # Generate and print report
    report = agent.generate_report()
    print(f"Overall Success: {report['summary']['overall_success']}")
```

### Advanced Usage

```python
from git_sandbox_agent.core.agent import GitSandboxAgent
from pathlib import Path

# Example 1: Using the default application-sandbox directory
with GitSandboxAgent() as agent:
    # Set up sandbox with a repository
    sandbox_path = agent.setup_sandbox("https://github.com/example/repo.git")
    
    # Run validation with custom commands
    validation_results = agent.run_validation(
        # Custom test command
        test_command=["pytest", "-xvs"],
        
        # Custom linter command
        linter_command=["flake8"],
        
        # Custom scripts to run
        custom_scripts=[
            {
                "path": "scripts/custom_validation.py",
                "args": ["--verbose"]
            }
        ]
    )
    
    # Generate report
    report = agent.generate_report()

# Example 2: Using a custom working directory
custom_dir = Path('/path/to/custom/directory')
with GitSandboxAgent(working_dir=custom_dir) as agent:
    # Set up sandbox with a repository in the custom directory
    sandbox_path = agent.setup_sandbox("https://github.com/example/repo.git")
    
    # Run validation tasks
    validation_results = agent.run_validation()
    
    # Note: Custom working directories are not automatically cleaned up
```

## Project Structure

```
git-sandbox-agent/
├── core/               # Core agent logic
│   ├── __init__.py
│   └── agent.py       # Main agent implementation
├── tools/             # Low-level tools and utilities
│   ├── __init__.py
│   ├── git_ops.py     # Git operations (clone only)
│   ├── sandbox_manager.py  # Sandbox creation/cleanup
│   └── validation.py  # Test and linting tools
├── tests/             # Unit tests
├── context/           # Shared state and configuration
├── output/            # Result handling and logs
├── prompts/           # Template messages for LLMs
├── example.py         # Example usage
└── requirements.txt   # Dependencies
```

## Limitations

This agent is intentionally limited to only clone repositories. It does not support:

- Checking out different branches after cloning
- Merging branches
- Modifying repository contents

These limitations are by design to ensure the agent only performs validation tasks in a clean environment without making any changes to the repository.

## Sandbox Directory

By default, all sandbox operations take place in the `application-sandbox` directory in the root. This directory is structured as follows:

```
application-sandbox/
u251cu2500u2500 sandbox-12345678/  # Unique ID for each sandbox instance
u251cu2500u2500 sandbox-87654321/  # Another sandbox instance
u2514u2500u2500 ...
```

Each sandbox gets its own directory with a unique identifier. These directories are automatically cleaned up when the agent is done with them.

You can also specify a custom working directory when initializing the agent, which will be used instead of creating a new directory in `application-sandbox`. Custom working directories are not automatically cleaned up.
