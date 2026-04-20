[![Tests](https://github.com/lc-rezende/Check-Git-Repo-Status/actions/workflows/test.yml/badge.svg)](https://github.com/lc-rezende/Check-Git-Repo-Status/actions/workflows/test.yml)

# Check Git Repo Status

A Python tool to scan git repositories and identify:
- Repositories **not linked to GitHub** (no GitHub remote configured)
- Repositories **with unpushed changes** (local commits not pushed to GitHub)

## Features

- Scans single repositories or directories containing multiple repositories
- Detects GitHub remotes (both SSH and HTTPS)
- Shows number of unpushed commits
- Displays branch tracking status
- Shows last unpushed commit information
- Handles edge cases (no commits, detached HEAD, missing upstream)

## Installation

Using [uv](https://github.com/astral-sh/uv):

```bash
cd ~/Documents/workspace/Check-Git-Repo-Status
uv run check-repo-status --help
```

Or install locally:

```bash
uv pip install -e .
```

## Usage

### Check current directory
```bash
uv run check-repo-status
```

### Check specific path
```bash
# Check entire workspace
uv run check-repo-status --path ~/Documents/workspace

# Check subdirectory
uv run check-repo-status -p ~/Documents/workspace/archive

# Check single repository
uv run check-repo-status -p ~/Documents/workspace/my-project
```

## Example Output

```
================================================================================
Git Repository Status Report
================================================================================

Target path: /Users/user/Documents/workspace
Total repositories scanned: 45

Repositories NOT linked to GitHub:
--------------------------------------------------------------------------------
  /Users/user/Documents/workspace/InitFileTest
  /Users/user/Documents/workspace/LocalProject

Repositories with unpushed changes:
--------------------------------------------------------------------------------
  /Users/user/Documents/workspace/jornada/demo-dbt
    → 2 commit(s) ahead
    → Tracking: No upstream tracking configured
    → Last commit: abc1234 - Add new feature (2 days ago)

  /Users/user/Documents/workspace/my-project
    → 5 commit(s) ahead
    → Tracking: Upstream: origin/main
    → Last commit: def5678 - Fix bug in parser (3 hours ago)
```

## Requirements

- Python 3.9+
- Git installed and in PATH

## How It Works

1. **Repository Discovery**: Recursively finds all `.git` directories
2. **Remote Detection**: Checks `git remote -v` for `github.com`
3. **Unpushed Commits**: Compares local branch with remote tracking branch
4. **Status Reporting**: Groups repos by issue type with detailed information

## Edge Cases Handled

- Repositories with no commits yet
- Detached HEAD states
- Branches without upstream tracking
- Branches never pushed to remote
- Multiple remote configurations
- Non-git directories (gracefully ignored)
