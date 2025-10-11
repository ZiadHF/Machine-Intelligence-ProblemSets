#!/bin/bash

echo "===== RUNNING AUTO-GRADER ====="

status_file="grading_status.txt"
> "$status_file"

failed_any=0
for dir in psets/*/; do
    [ -d "$dir" ] || continue
    echo "===== GRADING ${dir} ====="

    (cd "$dir" && python3 autograder.py) > "${dir%/}/grader_output.log" 2>&1
    
    file_read=$(cat "${dir%/}/grader_output.log")

    if echo "$file_read" | grep -q "FAIL"; then
        echo "${dir} FAILED"
        echo "${dir}: FAIL" >> "$status_file"
        failed_any=1
    else
        echo "${dir} PASSED"
        echo "${dir}: PASS" >> "$status_file"
    fi

    echo "----- LOG OUTPUT -----"
    cat "${dir%/}/grader_output.log"

    # Delete log file
    rm "${dir%/}/grader_output.log"

    echo "==============================="
done

# Exit non-zero if any problem set failed so CI will report failure
if [[ $failed_any -ne 0 ]]; then
    echo "One or more problem sets failed. Exiting with non-zero status."
    exit 2
fi

echo "===== AUTO-GRADER FINISHED ====="
if grep -q "FAIL" "$status_file"; then
    echo -e "Some problem sets failed. Please check the logs above."
else
    echo -e "All problem sets passed!"
fi
