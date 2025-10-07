---
description: Run code quality checks
---

Run all code quality tools: Black formatter, Flake8 linter, and Vulture dead code detector.

echo "Running Black..." && black --check . && echo "Running Flake8..." && flake8 && echo "Running Vulture..." && vulture --min-confidence 80
