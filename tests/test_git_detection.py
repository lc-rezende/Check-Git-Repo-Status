"""Tests for git repository detection."""

from check_repo_status.main import is_git_repository


def test_is_git_repository_with_git_dir(temp_git_repo):
    """Test that a directory with .git is detected as a git repository."""
    assert is_git_repository(temp_git_repo) is True


def test_is_git_repository_without_git_dir(temp_non_git_dir):
    """Test that a directory without .git is not detected as a git repository."""
    assert is_git_repository(temp_non_git_dir) is False
