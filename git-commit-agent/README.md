# Git Commit Agent

## Overview

The Git Commit Agent is a specialized agent for managing Git commits and branches. It provides a clean, modular interface for common Git operations related to committing and pushing changes.

## Features

- **Branch Management**:
  - Create new branches from any base branch
  - Checkout existing branches

- **Commit Operations**:
  - Stage specific files or all changes
  - Create commits with custom messages
  - Get commit hash and status information

- **Remote Operations**:
  - Push changes to remote repositories
  - Support for custom remote names

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from pathlib import Path
from core.agent import GitCommitAgent

# Initialize the agent with a repository path
repo_path = Path('/path/to/repo')
agent = GitCommitAgent(repo_path)

# Create a new branch
agent.create_branch('feature/new-feature', 'main')

# Stage all changes
agent.stage_all()

# Create a commit
agent.commit('Add new feature implementation')

# Push changes
agent.push()

# Get status information
status = agent.get_status()
print(f"Commit hash: {status['commit_hash']}")
```

### Simplified Function

For simple operations, use the `commit_and_push` helper function:

```python
from pathlib import Path
from core.agent import commit_and_push

repo_path = Path('/path/to/repo')
result = commit_and_push(
    repo_dir=repo_path,
    commit_message='Update documentation',
    create_branch=True,
    branch='feature/docs-update',
    base_branch='main',
    push=True
)

if result['success']:
    print(f"Successfully committed and pushed to {result['branch']}")
    print(f"Commit hash: {result['commit_hash']}")
else:
    print(f"Operation failed: {result['error']}")
```

## Environment Configuration

The agent uses environment variables from a central `.env` file in the project root and an agent-specific `.env` file. Required variables include:

- `GITHUB_TOKEN`: GitHub API token for authentication
- `GIT_AUTHOR_NAME`: Git author name
- `GIT_AUTHOR_EMAIL`: Git author email

## Example

Run the included example script to see the agent in action:

```bash
python example.py
```

This will demonstrate:
1. Creating a sandbox environment
2. Cloning a repository
3. Creating a new branch
4. Making changes to files
5. Staging and committing changes
6. Pushing changes to a remote repository

## Integration with Git Orchestrator

This agent is designed to be used as part of the Git Orchestrator workflow, which coordinates multiple Git agents to perform complex Git operations.
