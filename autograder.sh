#!/bin/bash

echo "===== RUNNING AUTO-GRADER ====="

status_file="grading_status.txt"
> "$status_file"

find psets -mindepth 1 -maxdepth 1 -type d | while IFS= read -r dir; do
    echo "===== GRADING ${dir} ====="

    set +e
    python3 autograder.py > "${dir}/grader_output.log" 2>&1
    exit_code=$?
    set -e

    if [[ $exit_code -eq 0 ]]; then
        echo -e "${dir} PASSED"
        echo "${dir}: PASS" >> "$status_file"
    else
        echo -e "${dir} FAILED (exit code $exit_code)"
        echo "${dir}: FAIL" >> "$status_file"
    fi

    cat "${dir}/grader_output.log"
    echo "==============================="
done

echo "===== AUTO-GRADER FINISHED ====="
if grep -q "FAIL" "$status_file"; then
    echo -e "Some problem sets failed. Please check the logs above."
else
    echo -e "All problem sets passed!"
fi
