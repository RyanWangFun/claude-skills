#!/bin/bash

# Add Command Logic

TASK_TITLE=""
TARGET_LIST=""
TASK_NOTES=""
DUE_DATE=""
DUE_TIME=""
PRIORITY="0"
TASK_URL=""
FLAGGED="false"

# Parse first positional argument as title
if [[ -n "$1" && ! "$1" =~ ^-- ]]; then
    TASK_TITLE="$1"
    shift
fi

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --list)
            TARGET_LIST="$2"
            shift 2
            ;;
        --notes)
            TASK_NOTES="$2"
            shift 2
            ;;
        --due)
            DUE_DATE="$2"
            shift 2
            ;;
        --priority)
            PRIORITY=$(parse_priority "$2")
            shift 2
            ;;
        --time)
            DUE_TIME="$2"
            shift 2
            ;;
        --url)
            TASK_URL="$2"
            shift 2
            ;;
        --flagged)
            FLAGGED="true"
            shift
            ;;
        *)
            error_exit "Unknown option: $1"
            ;;
    esac
done

if [[ -z "$TASK_TITLE" ]]; then
    error_exit "Task title is required. Usage: ... add <title> [options]"
fi

# robustly find the directory of this script (lib directory)
LIB_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SWIFT_SCRIPT="$LIB_DIR/add_task.swift"

if [[ ! -f "$SWIFT_SCRIPT" ]]; then
    error_exit "Helper script add_task.swift not found."
fi

# Build Swift command args
CMD_ARGS=("$TASK_TITLE")

if [[ -n "$TARGET_LIST" ]]; then
    CMD_ARGS+=("--list" "$TARGET_LIST")
fi

if [[ -n "$TASK_NOTES" ]]; then
    CMD_ARGS+=("--notes" "$TASK_NOTES")
fi

if [[ "$PRIORITY" != "0" ]]; then
    CMD_ARGS+=("--priority" "$PRIORITY")
fi

if [[ -n "$DUE_DATE" ]]; then
    CMD_ARGS+=("--due" "$DUE_DATE")
fi

if [[ -n "$DUE_TIME" ]]; then
    CMD_ARGS+=("--time" "$DUE_TIME")
fi

if [[ -n "$TASK_URL" ]]; then
    CMD_ARGS+=("--url" "$TASK_URL")
fi

if [[ "$FLAGGED" == "true" ]]; then
    CMD_ARGS+=("--flagged")
fi

# Execute Swift script
swift "$SWIFT_SCRIPT" "${CMD_ARGS[@]}"

if [[ $? -ne 0 ]]; then
    # Error message logic handled by Swift script (output to stderr) or we can customize generic error
    # but the swift script logs "❌ Error: ..."
    exit 1
fi

