#!/usr/bin/env python3
"""
Git Repository Status Checker

Scans directories for git repositories and checks:
1. Whether they have GitHub remotes configured
2. Whether they have unpushed commits to their GitHub remotes
"""

import argparse
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class RepoStatus:
    """Status information for a git repository."""
    path: str
    has_github_remote: bool
    unpushed_commits: int
    tracking_status: str
    last_commit_info: Optional[str]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Check git repositories for GitHub remotes and unpushed changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            %(prog)s                                    # Check current directory
            %(prog)s --path ~/Documents/workspace       # Check specific directory
            %(prog)s -p ~/workspace/my-project          # Check single repository
        """
    )
    parser.add_argument(
        "-p", "--path",
        type=str,
        help="Path to check (single repo or directory containing repos). Defaults to current directory."
    )
    return parser.parse_args()


def determine_target_path(provided_path: Optional[str]) -> Path:
    """
    Determine the target path to check.

    If no path is provided, use current working directory.
    Expand ~ and resolve to absolute path.
    """
    if provided_path:
        path = Path(provided_path).expanduser().resolve()
    else:
        path = Path.cwd()

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: Path is not a directory: {path}", file=sys.stderr)
        sys.exit(1)

    return path


def is_git_repository(path: Path) -> bool:
    """Check if a path is a git repository (has .git directory)."""
    return (path / ".git").exists()


def find_git_repos(target_path: Path) -> List[Path]:
    """
    Find all git repositories in the target path.

    If target_path itself is a git repo, return it as a single-item list.
    Otherwise, search recursively for all git repositories.
    """
    if is_git_repository(target_path):
        return [target_path]

    # Find all .git directories recursively
    try:
        result = subprocess.run(
            ["find", str(target_path), "-name", ".git", "-type", "d"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"Warning: Error searching for repositories: {result.stderr}", file=sys.stderr)
            return []

        # Extract parent directories of .git folders
        git_dirs = result.stdout.strip().split('\n')
        repos = [Path(d).parent for d in git_dirs if d]
        return sorted(repos)

    except subprocess.TimeoutExpired:
        print("Error: Search timed out after 30 seconds", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error: Failed to search for repositories: {e}", file=sys.stderr)
        return []


def has_github_remote(repo_path: Path) -> bool:
    """Check if repository has a GitHub remote configured."""
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return False

        # Check if any remote URL contains github.com
        return "github.com" in result.stdout

    except Exception:
        return False


def get_unpushed_status(repo_path: Path) -> Tuple[int, str, Optional[str]]:
    """
    Get unpushed commit status for a repository.

    Returns:
        Tuple of (commit_count, tracking_status_message, last_commit_info)
    """
    try:
        # Check if HEAD exists (repository has commits)
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            timeout=5
        )

        if result.returncode != 0:
            return 0, "No commits yet", None

        # Get current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return 0, "Unable to determine branch", None

        branch = result.stdout.strip()

        if branch == "HEAD":
            return 0, "Detached HEAD state", None

        # Try to get upstream tracking branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Has upstream tracking - use rev-list to count commits
            upstream = result.stdout.strip()

            result = subprocess.run(
                ["git", "rev-list", "--count", "--left-right", "@{upstream}...HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                behind, ahead = map(int, result.stdout.strip().split())

                if ahead > 0:
                    # Get last commit info
                    last_commit = get_last_commit_info(repo_path)
                    return ahead, f"Upstream: {upstream}", last_commit

                return 0, f"Up to date with {upstream}", None

        # No upstream tracking - try manual comparison with origin/<branch>
        remote_branch = f"origin/{branch}"

        result = subprocess.run(
            ["git", "rev-parse", "--verify", remote_branch],
            cwd=repo_path,
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            # Remote branch exists - compare
            result = subprocess.run(
                ["git", "rev-list", f"{remote_branch}..HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                unpushed_commits = [c for c in result.stdout.strip().split('\n') if c]
                count = len(unpushed_commits)

                if count > 0:
                    last_commit = get_last_commit_info(repo_path)
                    return count, "No upstream tracking configured", last_commit

                return 0, "No upstream tracking but up to date", None

        # Remote branch doesn't exist - all local commits are unpushed
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            total_commits = int(result.stdout.strip())

            if total_commits > 0:
                last_commit = get_last_commit_info(repo_path)
                return total_commits, f"Branch '{branch}' never pushed to remote", last_commit

        return 0, "No commits", None

    except subprocess.TimeoutExpired:
        return 0, "Timeout checking status", None
    except Exception as e:
        return 0, f"Error: {str(e)}", None


def get_last_commit_info(repo_path: Path) -> Optional[str]:
    """Get information about the last commit."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%h - %s (%cr)", "-1"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()

        return None

    except Exception:
        return None


def format_report(target_path: Path, repos_no_github: List[str], repos_with_unpushed: List[RepoStatus]) -> None:
    """Format and print the status report."""
    separator = "=" * 80
    subseparator = "-" * 80

    print(separator)
    print("Git Repository Status Report")
    print(separator)
    print()

    # Calculate total repos
    total_repos = len(repos_no_github) + len(repos_with_unpushed)

    # Add repos that are up to date (not in either list)
    # This is implicit in the count but not explicit

    print(f"Target path: {target_path}")

    # Try to count all repos scanned
    all_repos = find_git_repos(target_path)
    print(f"Total repositories scanned: {len(all_repos)}")
    print()

    # Repositories NOT linked to GitHub
    print("Repositories NOT linked to GitHub:")
    print(subseparator)

    if not repos_no_github:
        print("  None")
    else:
        for repo in sorted(repos_no_github):
            print(f"  {repo}")

    print()

    # Repositories with unpushed changes
    print("Repositories with unpushed changes:")
    print(subseparator)

    if not repos_with_unpushed:
        print("  None")
    else:
        for status in sorted(repos_with_unpushed, key=lambda x: x.path):
            print(f"  {status.path}")
            print(f"    → {status.unpushed_commits} commit(s) ahead")
            print(f"    → Tracking: {status.tracking_status}")
            if status.last_commit_info:
                print(f"    → Last commit: {status.last_commit_info}")
            print()


def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    target_path = determine_target_path(args.path)

    # Find all git repositories
    repos = find_git_repos(target_path)

    if not repos:
        print(f"No git repositories found in: {target_path}")
        sys.exit(0)

    # Check each repository
    repos_no_github = []
    repos_with_unpushed = []

    for repo_path in repos:
        # Check for GitHub remote
        has_gh_remote = has_github_remote(repo_path)

        if not has_gh_remote:
            repos_no_github.append(str(repo_path))
        else:
            # Check for unpushed commits
            count, tracking_status, last_commit = get_unpushed_status(repo_path)

            if count > 0:
                repos_with_unpushed.append(RepoStatus(
                    path=str(repo_path),
                    has_github_remote=True,
                    unpushed_commits=count,
                    tracking_status=tracking_status,
                    last_commit_info=last_commit
                ))

    # Print report
    format_report(target_path, repos_no_github, repos_with_unpushed)


if __name__ == "__main__":
    main()
