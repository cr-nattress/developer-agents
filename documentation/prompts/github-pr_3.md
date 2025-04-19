Create a Python module called `github_api.py` that uses the `PyGithub` library to create a pull request.

Add a function:
```python
def create_pull_request(token: str, repo_name: str, base: str, head: str, title: str, body: str) -> str
