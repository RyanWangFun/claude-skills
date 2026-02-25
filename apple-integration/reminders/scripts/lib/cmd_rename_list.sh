
ID_OR_TITLE="$1"
NEW_TITLE="$2"

if [[ -z "$ID_OR_TITLE" || -z "$NEW_TITLE" ]]; then
    error_exit "Usage: reminders rename-list <id-or-title> <new-title>"
fi

# Call Swift script
swift "$SCRIPT_DIR/rename_calendar.swift" "$ID_OR_TITLE" "$NEW_TITLE"
