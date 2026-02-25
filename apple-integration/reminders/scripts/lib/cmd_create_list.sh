
TITLE=""
COLOR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --color)
            COLOR="$2"
            shift 2
            ;;
        *)
            if [[ -z "$TITLE" ]]; then
                TITLE="$1"
                shift
            else
                error_exit "Unknown argument: $1"
            fi
            ;;
    esac
done

if [[ -z "$TITLE" ]]; then
    error_exit "Usage: reminders create-list <name> [--color <hex>]"
fi

# Call Swift script
swift "$SCRIPT_DIR/create_calendar.swift" "$TITLE" "$COLOR"
