"""Tests for GitHub remote detection."""

from check_repo_status.main import has_github_remote


def test_has_github_remote_with_ssh(temp_git_repo_with_github_ssh):
    """Test that GitHub SSH remote is detected."""
    assert has_github_remote(temp_git_repo_with_github_ssh) is True


def test_has_github_remote_with_https(temp_git_repo_with_github_https):
    """Test that GitHub HTTPS remote is detected."""
    assert has_github_remote(temp_git_repo_with_github_https) is True


def test_has_github_remote_with_gitlab(temp_git_repo_with_gitlab_remote):
    """Test that GitLab remote is not detected as GitHub."""
    assert has_github_remote(temp_git_repo_with_gitlab_remote) is False


def test_has_github_remote_with_no_remote(temp_git_repo_with_commit):
    """Test that repository with no remotes returns False."""
    assert has_github_remote(temp_git_repo_with_commit) is False
