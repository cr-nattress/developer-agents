Create a file `core/agent.py` that defines a function `run_git_workflow()` which:

1. Creates a sandbox
2. Clones a repo using `git_ops.clone_repo`
3. Creates a branch
4. Writes a test file to the repo folder
5. Commits and pushes changes
6. Creates a pull request via `github_api.create_pull_request`
7. Cleans up the sandbox

Make sure to call cleanup in a try/finally block.
