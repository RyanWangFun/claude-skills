#!/bin/bash

# Shared Utilities for Reminders Skill

# Error handling
error_exit() {
    echo "❌ Error: $1" >&2
    exit 1
}



# Convert priority string to AppleScript priority number
parse_priority() {
    local priority_str="$1"

    case "$priority_str" in
        "high"|"h"|"9")
            echo "9"
            ;;
        "medium"|"med"|"m"|"5")
            echo "5"
            ;;
        "low"|"l"|"1")
            echo "1"
            ;;
        "none"|"0"|"")
            echo "0"
            ;;
        *)
            error_exit "Invalid priority: $priority_str. Use: high, medium, low, or none"
            ;;
    esac
}

# Format priority for display
format_priority() {
    local priority="$1"

    case "$priority" in
        "9")
            echo "[!高]"
            ;;
        "5")
            echo "[!中]"
            ;;
        "1")
            echo "[!低]"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Format date for display
format_date() {
    local date_str="$1"

    if [[ "$date_str" != "missing value" ]]; then
        # Extract date components using AppleScript
        local formatted=$(osascript -e "set d to date \"$date_str\"
        return (year of d as string) & \"-\" & (text -2 thru -1 of (\"0\" & (month of d as integer))) & \"-\" & (text -2 thru -1 of (\"0\" & day of d))" 2>/dev/null)

        if [[ -n "$formatted" ]]; then
            echo "📅 $formatted"
        fi
    fi
}
