# CI output (snapshots)

This folder contains **plain-text snapshots** of selected CI job outputs.
The corresponding `.txt` files are included as submission evidence and can be read without running the project.

## Files

- `lint_output.txt`
  - Output from the linter step (Pylint).

- `unit_output.txt`
  - Output from running the unit test suite.

- `integration_output.txt`
  - Output from running the integration test suite.

## How these files are produced

In GitHub Actions, the CI workflow captures the console output for each step and uploads it as an artifact.
These files are copies of that output placed here for documentation/submission convenience.