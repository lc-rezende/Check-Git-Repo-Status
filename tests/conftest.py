"""Pytest fixtures for creating temporary git repositories."""

import subprocess

import pytest


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repository."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True
    )

    return repo_path


@pytest.fixture
def temp_git_repo_with_commit(temp_git_repo):
    """Create a temporary git repository with an initial commit."""
    # Create a file and commit it
    test_file = temp_git_repo / "test.txt"
    test_file.write_text("test content")

    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=temp_git_repo,
        check=True,
        capture_output=True
    )

    return temp_git_repo


@pytest.fixture
def temp_git_repo_with_github_ssh(temp_git_repo_with_commit):
    """Create a temporary git repository with GitHub SSH remote."""
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:user/repo.git"],
        cwd=temp_git_repo_with_commit,
        check=True,
        capture_output=True
    )
    return temp_git_repo_with_commit


@pytest.fixture
def temp_git_repo_with_github_https(temp_git_repo_with_commit):
    """Create a temporary git repository with GitHub HTTPS remote."""
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/user/repo.git"],
        cwd=temp_git_repo_with_commit,
        check=True,
        capture_output=True
    )
    return temp_git_repo_with_commit


@pytest.fixture
def temp_git_repo_with_gitlab_remote(temp_git_repo_with_commit):
    """Create a temporary git repository with GitLab remote."""
    subprocess.run(
        ["git", "remote", "add", "origin", "https://gitlab.com/user/repo.git"],
        cwd=temp_git_repo_with_commit,
        check=True,
        capture_output=True
    )
    return temp_git_repo_with_commit


@pytest.fixture
def temp_non_git_dir(tmp_path):
    """Create a temporary directory that is not a git repository."""
    non_repo_path = tmp_path / "non_repo"
    non_repo_path.mkdir()
    return non_repo_path
