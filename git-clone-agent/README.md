# Git Clone Agent

A Python agent for cloning Git repositories into a sandbox environment. This agent focuses specifically on cloning repositories from GitHub and other remote sources. All clone operations take place in the `application-sandbox` directory in the root by default.

## Features

- Clone repositories from GitHub and other remote sources
- Optionally specify branches to checkout
- Set up Git configuration (user.name, user.email)
- Automatic sandbox environment management
- Clean error handling and status reporting

## Installation

```bash
# Clone the repository
git clone https://github.com/cr-nattress/dev-agents.git
cd dev-agents/git-clone-agent

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from git_clone_agent.core.agent import GitCloneAgent

# Use the agent as a context manager for automatic cleanup
with GitCloneAgent() as agent:
    # Clone a repository
    success, clone_dir = agent.clone_repository(
        repo_url="https://github.com/example/repo.git",
        branch="main"  # Optional
    )
    
    if success:
        print(f"Repository cloned to {clone_dir}")
    else:
        print(f"Clone failed: {agent.get_status().get('error')}")
```

### Advanced Usage

```python
from git_clone_agent.core.agent import GitCloneAgent
from pathlib import Path

# Example 1: Using the default application-sandbox directory with custom Git config
git_config = {
    "user.name": "Your Name",
    "user.email": "your.email@example.com"
}

with GitCloneAgent() as agent:
    success, clone_dir = agent.clone_repository(
        repo_url="https://github.com/example/repo.git",
        branch="develop",
        git_config=git_config
    )
    
    # Check status
    status = agent.get_status()
    print(f"Clone status: {status}")

# Example 2: Using a custom working directory
custom_dir = Path('/path/to/custom/directory')
with GitCloneAgent(working_dir=custom_dir) as agent:
    agent.clone_repository("https://github.com/example/repo.git")
    
    # Note: Custom working directories are not automatically cleaned up
```

## Project Structure

```
git-clone-agent/
├── core/               # Core agent logic
│   ├── __init__.py
│   └── agent.py       # Main agent implementation
├── tools/             # Low-level tools and utilities
│   ├── __init__.py
│   ├── git_ops.py     # Git operations
│   └── sandbox_manager.py  # Sandbox creation/cleanup
├── tests/             # Unit tests
├── context/           # Shared state and configuration
├── output/            # Result handling and logs
├── prompts/           # Template messages for LLMs
├── example.py         # Example usage
└── requirements.txt   # Dependencies
```

## Sandbox Directory

By default, all clone operations take place in the `application-sandbox` directory in the root. This directory is structured as follows:

```
application-sandbox/
├── repo-example/      # Named after the repository
├── repo-custom-name/  # Custom name if provided
└── repo-12345678/     # UUID-based name if no name is provided
```

Each repository gets its own directory. When using the agent as a context manager, these directories are automatically cleaned up when the agent is done with them.

You can also specify a custom working directory when initializing the agent, which will be used instead of creating a new directory in `application-sandbox`. Custom working directories are not automatically cleaned up.
