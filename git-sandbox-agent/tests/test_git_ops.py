import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from git_sandbox_agent.tools import git_ops


class TestGitOps(unittest.TestCase):
    
    @patch('subprocess.run')
    def test_run_git_command(self, mock_run):
        # Setup mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "command output"
        mock_run.return_value = mock_process
        
        # Test successful command
        cwd = Path('/tmp/sandbox')
        result = git_ops.run_git_command(["status"], cwd)
        
        # Verify
        mock_run.assert_called_once_with(
            ["git", "status"], 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        self.assertEqual(result, "command output")
    
    @patch('subprocess.run')
    def test_run_git_command_error(self, mock_run):
        # Setup mock for error
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "error message"
        mock_run.return_value = mock_process
        
        # Test command that fails
        cwd = Path('/tmp/sandbox')
        with self.assertRaises(RuntimeError) as context:
            git_ops.run_git_command(["invalid-command"], cwd)
        
        # Verify error message
        self.assertIn("error message", str(context.exception))
    
    @patch('git_sandbox_agent.tools.git_ops.run_git_command')
    def test_clone_repo(self, mock_run_git_command):
        # Setup
        mock_run_git_command.return_value = "Cloning into 'repo'..."
        repo_url = "https://github.com/example/repo.git"
        target_dir = Path('/tmp/sandbox')
        
        # Test without branch
        result = git_ops.clone_repo(repo_url, target_dir)
        
        # Verify
        mock_run_git_command.assert_called_once_with(
            ["clone", repo_url, "."], 
            cwd=target_dir
        )
        self.assertEqual(result, "Cloning into 'repo'...")
    
    @patch('git_sandbox_agent.tools.git_ops.run_git_command')
    def test_clone_repo_with_branch(self, mock_run_git_command):
        # Setup
        mock_run_git_command.return_value = "Cloning into 'repo'..."
        repo_url = "https://github.com/example/repo.git"
        target_dir = Path('/tmp/sandbox')
        branch = "feature-branch"
        
        # Test with branch
        result = git_ops.clone_repo(repo_url, target_dir, branch)
        
        # Verify
        mock_run_git_command.assert_called_once_with(
            ["clone", repo_url, ".", "--branch", branch], 
            cwd=target_dir
        )
        self.assertEqual(result, "Cloning into 'repo'...")


if __name__ == '__main__':
    unittest.main()
