#!/bin/bash
# Edit wrapper

# Directory of this script
LIB_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EDIT_BIN="$LIB_DIR/edit_task"

if [[ ! -f "$EDIT_BIN" ]]; then
    # Fallback to swift script execution if binary missing?
    # Better to fail or compile-on-fly, but keeping simple
    if [[ -f "$LIB_DIR/edit_task.swift" ]]; then
        swift "$LIB_DIR/edit_task.swift" "$@"
    else
        echo "Error: edit_task binary or script not found." >&2
        exit 1
    fi
else
    "$EDIT_BIN" "$@"
fi
