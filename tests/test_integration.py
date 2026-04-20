"""Integration tests for repository scanning."""

import subprocess

from check_repo_status.main import find_git_repos, has_github_remote


def test_single_repo_scan(temp_git_repo_with_github_ssh):
    """Test scanning a single repository with GitHub remote."""
    # Find repos
    repos = find_git_repos(temp_git_repo_with_github_ssh)

    # Should find exactly one repo
    assert len(repos) == 1
    assert repos[0] == temp_git_repo_with_github_ssh

    # Should have GitHub remote
    assert has_github_remote(repos[0]) is True


def test_repos_without_github_remote(tmp_path):
    """Test identifying repositories without GitHub remote."""
    # Create multiple repos: some with GitHub, some without
    repo1 = tmp_path / "repo1"
    repo2 = tmp_path / "repo2"
    repo3 = tmp_path / "repo3"

    for repo in [repo1, repo2, repo3]:
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo,
            check=True,
            capture_output=True
        )

    # Add GitHub remote to repo1 and repo2
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:user/repo1.git"],
        cwd=repo1,
        check=True,
        capture_output=True
    )
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/user/repo2.git"],
        cwd=repo2,
        check=True,
        capture_output=True
    )

    # repo3 has no remote

    # Find all repos
    repos = find_git_repos(tmp_path)
    assert len(repos) == 3

    # Check which have GitHub remotes
    repos_with_github = [repo for repo in repos if has_github_remote(repo)]
    repos_without_github = [repo for repo in repos if not has_github_remote(repo)]

    # Should have 2 with GitHub, 1 without
    assert len(repos_with_github) == 2
    assert len(repos_without_github) == 1

    # Verify the one without is repo3
    assert repo3 in repos_without_github
