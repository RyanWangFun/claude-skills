
ID_OR_TITLE="$1"
FORCE=false

if [[ "$2" == "--force" ]]; then
    FORCE=true
fi

if [[ -z "$ID_OR_TITLE" ]]; then
    error_exit "Usage: reminders delete-list <id-or-title> [--force]"
fi

# 1. Check list details (dry run)
OUTPUT=$(swift "$SCRIPT_DIR/delete_calendar.swift" "$ID_OR_TITLE" 2>&1)
if [ $? -ne 0 ]; then
    echo "$OUTPUT"
    exit 1
fi

echo "$OUTPUT"
# Extract task count (simple grep/awk)
TASK_COUNT=$(echo "$OUTPUT" | grep "Tasks:" | awk '{print $2}')

if [[ "$FORCE" == "false" ]]; then
    if [[ "$TASK_COUNT" -gt 0 ]]; then
        echo "WARNING: This list contains $TASK_COUNT tasks. Deleting it will delete ALL tasks inside."
    fi
    read -p "Are you sure you want to delete this list? (y/N): " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "Operation cancelled."
        exit 0
    fi
fi

# 2. Execute deletion
swift "$SCRIPT_DIR/delete_calendar.swift" "$ID_OR_TITLE" "--execute"
