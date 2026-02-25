#!/bin/bash

# Reminders Management Script
# Dynamically generates and executes AppleScript commands for macOS Reminders

# Determine script directory to source lib files relative to it
SCRIPT_DIR="$(dirname "$0")"

# Source shared utilities
source "$SCRIPT_DIR/lib/common.sh"

OPERATION="${1:-}"

# Usage information
usage() {
    cat <<EOF
Usage: $0 <operation> [arguments]

Operations:
  list [list-name]              List all tasks or tasks from a specific list
  list-lists                    List all calendar/lists with details
  create-list <name> [--color]  Create a new list
  rename-list <id|name> <new>   Rename a list
  delete-list <id|name>         Delete a list
  add <title> [options]         Add a new task with optional details
   edit <id|title> [options]     Edit task properties
  delete <id|title>             Delete a task (permanent)
  search <keyword>              Search for tasks by keyword

Add Options:
  --list <name>                 List to add task to (default: first list)
  --notes <text>                Task notes/description
  --due <date>                  Due date (format: YYYY-MM-DD or "tomorrow" or "next week")
  --time <HH:mm>                Specific time (e.g. 14:00)
  --priority <level>            Priority: high, medium, low, or none (default)
  --url <url>                   Attach a URL
  --flagged                     Flag the task

Edit Options:
  --new-title <text>            Update title
  --move-to-list <name>         Move task to another list
  --flagged / --unflagged       Set flag status
  (plus --notes, --due, --time, --priority, --url)

Examples:
  $0 list
  $0 list "01Projects"
  $0 add "Review PR" --list "Work" --notes "Check auth changes" --due "2026-01-15" --priority high
  $0 add "Buy groceries" --due tomorrow --priority low
  $0 done "Review PR"
  $0 search "PR"
  $0 edit "Review PR" --flagged
  $0 delete "Buy groceries"
EOF
    exit 1
}

# Validate operation
if [[ -z "$OPERATION" ]]; then
    usage
fi

case "$OPERATION" in
    list)
        shift # Remove 'list'
        source "$SCRIPT_DIR/lib/cmd_list.sh" "$@"
        ;;
    list-lists)
        shift # Remove 'list-lists'
        source "$SCRIPT_DIR/lib/cmd_list_lists.sh"
        ;;
    create-list)
        shift # Remove 'create-list'
        source "$SCRIPT_DIR/lib/cmd_create_list.sh"
        ;;
    rename-list)
        shift # Remove 'rename-list'
        source "$SCRIPT_DIR/lib/cmd_rename_list.sh"
        ;;
    delete-list)
        shift # Remove 'delete-list'
        source "$SCRIPT_DIR/lib/cmd_delete_list.sh"
        ;;
    add)
        shift # Remove 'add'
        source "$SCRIPT_DIR/lib/cmd_add.sh"
        ;;
    edit)
        shift
        source "$SCRIPT_DIR/lib/cmd_edit.sh"
        ;;
    delete)
        shift
        source "$SCRIPT_DIR/lib/cmd_delete.sh"
        ;;
    done)
        shift # Remove 'done'
        source "$SCRIPT_DIR/lib/cmd_done.sh"
        ;;
    search)
        shift # Remove 'search'
        source "$SCRIPT_DIR/lib/cmd_search.sh"
        ;;
    *)
        error_exit "Unknown operation: $OPERATION"
        ;;
esac
