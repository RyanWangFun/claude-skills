---
name: reminders
description: "Comprehensive macOS Reminders management with full task and list CRUD. Task operations: list, add, edit, delete, complete, search. Rich metadata: priority, due date+time, notes, URL, flagged. List operations: list-lists, create-list, rename-list, delete-list. Task movement between lists. Use when user needs to: (1) View/search tasks or lists, (2) Create/modify tasks or lists, (3) Edit task properties or move tasks between lists, (4) Complete or delete tasks/lists, (5) Manage reminders from conversation context."
---

# Reminders Management

Seamless integration with macOS Reminders app for task management through conversational commands.

## Quick Reference

Execute the skill with subcommands:

```bash
scripts/reminders.sh <operation> [arguments]
```

**Available Operations:**

- `list [list-name]` - View all tasks or filter by list
- `list-lists` - View all available lists
- `create-list <name> [--color]` - Create a new list
- `rename-list <id|name> <new>` - Rename a list
- `delete-list <id|name>` - Delete a list
- `add <title> [options]` - Create task with rich metadata (priority, due date+time, notes, URL, flagged)
- `edit <identifier> [options]` - Modify existing task properties (including moving lists)
- `done <task-name>` - Mark task as completed
- `delete <identifier>` - Remove task permanently
- `search <keyword>` - Find tasks by keyword

**Common Usage:**

```bash
# View tasks
scripts/reminders.sh list
scripts/reminders.sh list "Work"

# Create task (supports --list, --notes, --due, --time, --priority, --url, --flagged)
scripts/reminders.sh add "Review PR" --list "Work" --due tomorrow --time "14:00" --priority high --flagged

# Edit task (update properties)
scripts/reminders.sh edit "Review PR" --due "2026-01-20" --notes "Check auth changes"

# Move task to another list
scripts/reminders.sh edit "Review PR" --move-to-list "Personal"

# Complete task
scripts/reminders.sh done "Review PR"

# Delete task
scripts/reminders.sh delete "Old task"

# Search
scripts/reminders.sh search "meeting"
```

## Detailed Documentation

- **Full API Reference**: See [references/API.md](references/API.md) for complete parameter documentation
- **Usage Examples**: See [references/EXAMPLES.md](references/EXAMPLES.md) for workflow patterns and advanced usage
