# Worktree Error Prevention System

## Overview
A comprehensive git worktree management system designed to prevent data loss, clean up orphaned branches, and ensure build reliability.

## Key Features
- Automatic orphaned worktree detection and cleanup
- Stale lock removal
- Build failure atomic rollback
- Verbose error reporting

## Usage
Export `TREE_VERBOSE=1` for detailed logging
Use `--verbose` flag for runtime verbosity

## Installation
1. Place `tree.sh` in `.claude/scripts/`
2. Source script in your build process
3. Ensure executable permissions

## Contributing
See `CONTRIBUTING.md` for development guidelines
