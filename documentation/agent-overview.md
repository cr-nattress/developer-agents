# Git Agent Specifications

## git-clone-agent
**Purpose**: Clone a repository from a remote source.

**Responsibilities**:
- Accept repository URL and optional branch name.
- Clone the repository using `git clone`.
- Set up Git config (e.g., user.name, user.email).
- Verify credentials or access token if needed.
- Output local path and success/failure status.

---

## git-branch-agent
**Purpose**: Create a new branch based on a given base.

**Responsibilities**:
- Checkout the base branch (e.g., `main`, `develop`).
- Create a new branch (e.g., `feature/foo`).
- Optionally push the new branch to remote.
- Output new branch name and HEAD commit.

---

## git-commit-agent
**Purpose**: Stage, commit, and push code changes.

**Responsibilities**:
- Stage selected changes or all (`git add .`).
- Generate or accept a commit message.
- Create commit with `git commit`.
- Push to the remote branch.
- Output commit hash and status.

---

## git-pr-agent
**Purpose**: Open a pull request.

**Responsibilities**:
- Use API to create PR (GitHub, GitLab, etc).
- Set base and compare branches.
- Add title, description, labels, reviewers.
- Optionally apply a PR template.
- Output PR URL, ID, and status.

---

## git-sandbox-agent
**Purpose**: Run validation tasks in a clean environment.

**Responsibilities**:
- Set up sandbox environment (e.g., Docker, temp folder).
- Check out PR branch and simulate merge if needed.
- Run tests, linters, or CI scripts.
- Capture logs and output status.
- Generate summary report or artifacts.
