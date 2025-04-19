# Git Orchestrator Agent

A Python agent that coordinates the execution of specialized Git agents to perform a complete Git workflow. This agent focuses on orchestration rather than directly performing Git operations or file system management.

## Purpose

The Git Orchestrator Agent serves as a central coordinator that:

- Maintains state for the entire Git workflow
- Calls specialized agents to perform specific tasks
- Manages the workflow execution sequence
- Handles error conditions and cleanup

## Features

- Dynamically loads available Git agents
- Orchestrates a complete Git workflow from cloning to PR creation
- Maintains state between agent calls
- Provides detailed workflow results and status
- Ensures proper cleanup even if errors occur

## Installation

```bash
# Clone the repository
git clone https://github.com/cr-nattress/dev-agents.git
cd dev-agents/git-orchestrator-agent

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from git_orchestrator_agent.core.agent import run_git_workflow

# Run a complete Git workflow
result = run_git_workflow(
    repo_url="https://github.com/example/repo.git",
    branch_name="feature/new-feature",
    file_content="This is a test file.",
    commit_message="Add test file",
    pr_title="Add test file",
    pr_description="This PR adds a test file.",
    github_token="your-github-token"  # Optional
)

# Check the results
if result["success"]:
    print(f"Workflow completed successfully. PR URL: {result['pr_url']}")
else:
    print(f"Workflow failed: {result['error']}")
```

### Advanced Usage

```python
from git_orchestrator_agent.core.agent import GitOrchestratorAgent

# Create an orchestrator instance
orchestrator = GitOrchestratorAgent()

# Run the workflow
result = orchestrator.run_git_workflow(
    repo_url="https://github.com/example/repo.git",
    branch_name="feature/new-feature",
    file_content="This is a test file.",
    commit_message="Add test file",
    pr_title="Add test file",
    pr_description="This PR adds a test file."
)

# Examine the detailed workflow steps
for step in result["steps"]:
    print(f"Step: {step['step']}, Success: {step['success']}")
```

## Project Structure

```
git-orchestrator-agent/
├── core/               # Core agent logic
│   ├── __init__.py
│   └── agent.py       # Main orchestrator implementation
├── tools/             # Utility functions (empty - orchestrator doesn't perform operations directly)
│   └── __init__.py
├── tests/             # Unit tests
├── context/           # Shared state and configuration
├── output/            # Result handling and logs
├── prompts/           # Template messages for LLMs
├── example.py         # Example usage
└── requirements.txt   # Dependencies
```

## Agent Coordination

The Git Orchestrator Agent coordinates the following specialized agents:

1. **Git Clone Agent**: Clones repositories from remote sources
2. **Git Branch Agent**: Creates and manages branches
3. **Git Commit Agent**: Handles staging, committing, and pushing code changes
4. **Git PR Agent**: Automates pull request creation and management
5. **Git Sandbox Agent**: Manages the sandbox environment for testing

Each agent is responsible for a specific part of the Git workflow, and the orchestrator ensures they work together seamlessly.

## Error Handling

The orchestrator implements robust error handling to ensure that:

- Errors in any step are properly reported
- The workflow stops if a critical step fails
- Cleanup is performed even if errors occur
- Detailed error information is provided in the results

## State Management

The orchestrator maintains state between agent calls, including:

- Sandbox directory path
- Repository directory path
- Branch name
- Commit hash
- Other workflow-specific information

This state is used to pass information between agents and ensure the workflow proceeds correctly.
