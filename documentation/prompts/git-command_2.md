Create a Python module called `git_ops.py` in the `tools` directory that wraps basic Git commands using `subprocess.run`. The following functions should be included:

- `clone_repo(repo_url: str, target_dir: Path)`
- `create_branch(branch_name: str, cwd: Path)`
- `commit_all(message: str, cwd: Path)`
- `push_branch(branch_name: str, cwd: Path)`

All functions should raise `RuntimeError` if the git command fails, and return the command output otherwise.
