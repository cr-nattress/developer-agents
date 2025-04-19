# Coder Agent

A Python agent that uses OpenAI to analyze code and implement changes based on natural language prompts.

## Overview

The Coder Agent is designed to process a repository of Python code and make modifications based on natural language instructions. It works independently and communicates with the Agent Orchestrator.

## Features

- Recursively collects Python files from a repository (with configurable limits)
- Bundles code files into a structured format for LLM processing
- Uses OpenAI's API to generate code changes based on natural language prompts
- Applies changes to the original files
- Generates detailed reports of the modifications made

## Architecture

The agent follows a modular architecture:

- **Core**: Contains the main agent logic
- **Tools**: Specialized utilities for code collection, OpenAI integration, and code updating
- **Context**: Configuration and environment management
- **Tests**: Test cases for the agent functionality

## Requirements

- Python 3.8+
- OpenAI API key
- python-dotenv (for environment variable management)

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Set up your environment variables by creating a `.env` file in the agent directory:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Basic Usage

Run the example script to see the agent in action:

```bash
python example.py [repo_path] [prompt]
```

Where:
- `repo_path` is the path to the repository you want to process (defaults to the current directory)
- `prompt` is the natural language instruction for code changes (defaults to "Add docstrings to all functions that don't have them")

### Integration with Agent Orchestrator

The Coder Agent is designed to be used by the Agent Orchestrator. The orchestrator will:

1. Provide the repository path and prompt
2. Call the `process_repo` method
3. Receive the results and report

## Example Prompts

- "Add type annotations to all functions in utils/"
- "Refactor the calculator module to use a class-based approach"
- "Add error handling to all functions that might raise exceptions"
- "Optimize the performance of the data processing functions"
- "Convert all functions to use async/await pattern"

## Testing

Run the test suite to verify the agent's functionality:

```bash
python test_coder_agent.py
```

## Limitations

- Currently limited to processing Python files only
- Maximum of 5 files or 2000 lines of code in the initial version
- Depends on OpenAI's API availability and rate limits
