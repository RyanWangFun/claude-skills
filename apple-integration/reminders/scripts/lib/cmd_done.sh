#!/bin/bash

# Done Command Logic

TASK_NAME="${1:-}"

if [[ -z "$TASK_NAME" ]]; then
    error_exit "Task name is required. Usage: ... done <task-name>"
fi

# robustly find the directory of this script (lib directory)
LIB_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SWIFT_SCRIPT="$LIB_DIR/complete_task.swift"

if [[ ! -f "$SWIFT_SCRIPT" ]]; then
    error_exit "Helper script complete_task.swift not found."
fi

# Execute Swift script
swift "$SWIFT_SCRIPT" "$TASK_NAME"

if [[ $? -ne 0 ]]; then
    # Error will be printed by Swift script
    exit 1
fi

