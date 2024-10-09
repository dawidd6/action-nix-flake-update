#!/usr/bin/env bash

set -euo pipefail

# Simulate some of GitHub Actions environment.
export GITHUB_ACTION_PATH="${PWD}"
export GITHUB_OUTPUT=/dev/stdout
export GITHUB_SUMMARY=/dev/null

# Simulate GitHub Actions workspace.
cd test

# Clean up after script exit.
trap 'git checkout -- flake.lock' EXIT

# Retrieve expected and actual outputs.
expected_output="$(cat output.md)"
actual_output="$("${GITHUB_ACTION_PATH}"/main.py)"

echo "${actual_output}" > /tmp/test.txt
# Compare expected and actual outputs.
if [[ "${expected_output}" != "${actual_output}" ]]; then
    diff -u <(echo "${expected_output}") <(echo "${actual_output}") | cat -t
fi

if status="$(git status -s -u)"; [[ "${status}" != ' M flake.lock' ]]; then
    echo "${status}"
    exit 1
fi
