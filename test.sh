#!/usr/bin/env bash

set -euo pipefail

main_directory="${PWD}"
test_directory="${PWD}/test"

expected_github_output="${test_directory}/expected_github_output"
expected_github_summary="${test_directory}/expected_github_summary"

export GITHUB_ACTION_PATH="${main_directory}"
export GITHUB_OUTPUT="${test_directory}/actual_github_output"
export GITHUB_SUMMARY="${test_directory}/actual_github_summary"

function cleanup() {
    git checkout -- "${test_directory}/flake.lock"
    rm -f "${GITHUB_OUTPUT}"
    rm -f "${GITHUB_SUMMARY}"
}

trap cleanup EXIT

( cd "${test_directory}" && "${GITHUB_ACTION_PATH}"/main.py )

case "${1-}" in
    update)
        echo "Updating expected outputs..."
        cp "${GITHUB_OUTPUT}" "${expected_github_output}"
        cp "${GITHUB_SUMMARY}" "${expected_github_summary}"
    ;;
esac

diff -u "${expected_github_output}" "${GITHUB_OUTPUT}" | cat -t
diff -u "${expected_github_summary}" "${GITHUB_SUMMARY}" | cat -t
