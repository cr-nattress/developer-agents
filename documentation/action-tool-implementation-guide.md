# Action/Tool Layer - Implementation Guide

## Overview
The Action/Tool Layer is the execution engine of a focused AI agent. It is responsible for performing all concrete tasks, such as interacting with Git repositories, managing filesystems, and calling external APIs (e.g., GitHub). This document outlines how to structure and implement the Action/Tool Layer in Python for a Git automation agent.

---

## Responsibilities
- Perform Git operations (clone, branch, commit, push)
- Interact with GitHub via API (e.g., create pull requests)
- Manage a sandboxed working directory
- Maintain clear boundaries: no business logic or decision-making here

---

## Recommended Structure

```bash
tools/
├── git_ops.py             # Git command wrappers
├── github_api.py          # GitHub API helpers
├── sandbox_manager.py     # Folder creation/deletion
```

---

## 1. `git_ops.py`
### Purpose
Provides shell wrappers around Git commands for local repo manipulation.

### Implementation Notes
- Use `subprocess.run()` to call Git safely
- Accept a working directory as a parameter for all operations

### Example Functions
```python
import subprocess
from pathlib import Path

def run_git_command(args: list, cwd: Path):
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git failed: {result.stderr}")
    return result.stdout.strip()

def clone_repo(repo_url: str, target_dir: Path):
    return run_git_command(["clone", repo_url, "."], cwd=target_dir)

def create_branch(branch_name: str, cwd: Path):
    run_git_command(["checkout", "-b", branch_name], cwd=cwd)

def commit_all(message: str, cwd: Path):
    run_git_command(["add", "."], cwd=cwd)
    run_git_command(["commit", "-m", message], cwd=cwd)

def push_branch(branch_name: str, cwd: Path):
    run_git_command(["push", "-u", "origin", branch_name], cwd=cwd)
```

---

## 2. `github_api.py`
### Purpose
Handles communication with GitHub via API. Ideal for creating pull requests, fetching repo info, etc.

### Recommended Library
- `PyGithub`

### Example Function
```python
from github import Github

def create_pull_request(token, repo_name, base, head, title, body):
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.create_pull(title=title, body=body, base=base, head=head)
    return pr.html_url
```

---

## 3. `sandbox_manager.py`
### Purpose
Manages creation and cleanup of a temporary folder to hold the cloned repository.

### Example Functions
```python
import shutil
import tempfile
from pathlib import Path

def create_sandbox() -> Path:
    path = Path(tempfile.mkdtemp(prefix="git-agent-"))
    return path

def cleanup_sandbox(path: Path):
    shutil.rmtree(path, ignore_errors=True)
```

---

## Tech Stack Summary
| Task                   | Recommended Tool         |
|------------------------|--------------------------|
| Git operations         | `subprocess`, `GitPython` (optional)
| GitHub API             | `PyGithub`
| Sandbox management     | `tempfile`, `shutil`
| Config/environment     | `python-dotenv`

---

## Best Practices
- Keep each action atomic and testable
- Use exceptions to handle failures clearly
- Avoid embedding logic for tool choice in this layer — that's the Reasoning Layer's job
- Treat this layer like a CLI toolbox: it only does what it's told

---

## Next Steps
- Implement unit tests for each module using mock filesystem and API clients
- Integrate with Reasoning Layer for dynamic tool chaining
- Use `.env` and `python-dotenv` to manage GitHub tokens and Git config

---

## References
- [GitPython Docs](https://gitpython.readthedocs.io/)
- [PyGithub Docs](https://pygithub.readthedocs.io/)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
- [python-dotenv](https://saurabh-kumar.com/python-dotenv/)

---

This document is intended to be referenced by AI agents or developers when building or extending the execution capabilities of a Git-based automation agent.

