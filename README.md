# Dev Agents

A collection of specialized Git-focused agents designed to automate and streamline various aspects of the development workflow. Each agent is purpose-built to handle specific Git operations efficiently and reliably.

## Repository Structure

This repository contains several specialized agents:

- **git-clone-agent**: Clones repositories from remote sources with proper configuration
- **git-branch-agent**: Creates and manages branches based on a given base
- **git-commit-agent**: Handles staging, committing, and pushing code changes
- **git-pr-agent**: Automates pull request creation and management
- **git-sandbox-agent**: Runs validation tasks in a clean, isolated environment

## Sandbox Environment

The repository includes a shared `application-sandbox` directory in the root that provides an isolated environment for testing and validation. This directory is managed by the git-sandbox-agent and:

- Is automatically created if it doesn't exist
- Is cleaned up before each use if it already exists
- Contains separate subdirectories for each sandbox instance with unique identifiers

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git installed and configured
- Required Python packages (see individual agent requirements.txt files)

### Installation

```bash
# Clone the repository
git clone https://github.com/cr-nattress/dev-agents.git
cd dev-agents

# Install dependencies for a specific agent
cd git-sandbox-agent
pip install -r requirements.txt
```

## Usage Examples

### Git Sandbox Agent

```python
from git_sandbox_agent.core.agent import GitSandboxAgent

# Use the agent as a context manager for automatic cleanup
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

## Documentation

Detailed documentation for each agent can be found in the `documentation` directory:

- Agent specifications and responsibilities: [Agent Overview](documentation/agent-overview.md)
- Implementation guides: [Action Tool Implementation Guide](documentation/action-tool-implementation-guide.md)
- Prompt templates: [documentation/prompts/](documentation/prompts/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
