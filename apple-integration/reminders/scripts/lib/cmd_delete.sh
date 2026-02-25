#!/bin/bash
# Delete wrapper

# Directory of this script
LIB_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DELETE_BIN="$LIB_DIR/delete_task"

if [[ ! -f "$DELETE_BIN" ]]; then
    if [[ -f "$LIB_DIR/delete_task.swift" ]]; then
        swift "$LIB_DIR/delete_task.swift" "$@"
    else
        echo "Error: delete_task binary or script not found." >&2
        exit 1
    fi
else
    "$DELETE_BIN" "$@"
fi
