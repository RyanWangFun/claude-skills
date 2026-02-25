# Reminders API Reference

## Commands

### list

List tasks from Reminders app.

```bash
scripts/reminders.sh list [list-name]
```

**Arguments:**
- `[list-name]` (optional) - Filter by specific list name. If omitted, shows all tasks from all lists.

**Output:** Markdown-formatted list showing tasks organized by list.


---

### list-lists

List all available calendar lists.

```bash
scripts/reminders.sh list-lists
```

**Output:** Table showing list names, sources (iCloud/Local), IDs, and colors.

---

### create-list

Create a new calendar list.

```bash
scripts/reminders.sh create-list <name> [options]
```

**Arguments:**
- `<name>` (required) - Name of the new list.

**Options:**
- `--color <hex>` - Color for the list (e.g. #FF0000).

---

### rename-list

Rename an existing list.

```bash
scripts/reminders.sh rename-list <id|name> <new-name>
```

**Arguments:**
- `<id|name>` - Identifier or exact name of the list.
- `<new-name>` - New name for the list.

---

### delete-list

Delete a list and all its tasks.

```bash
scripts/reminders.sh delete-list <id|name> [--force]
```

**Arguments:**
- `<id|name>` - Identifier or exact name of the list.
- `--force` - Skip confirmation prompts.

---

### add

Create a new task with optional metadata.

```bash
scripts/reminders.sh add <title> [options]
```

**Arguments:**
- `<title>` (required) - Task title/description

**Options:**
- `--list <name>` - Target list (default: system default list)
- `--notes <text>` - Task notes/description
- `--due <date>` - Due date in format:
  - `YYYY-MM-DD` (e.g., "2026-01-20")
  - `today`
  - `tomorrow`
  - `next week`
- `--time <time>` - Due time in `HH:MM` format (e.g., "14:00", "09:30")
- `--priority <level>` - Priority level:
  - `high` (1)
  - `medium` (5)
  - `low` (9)
  - `none` (0, default)
- `--url <url>` - Associated URL/link
- `--flagged` - Mark task as flagged (important)

**Output:** Success confirmation with task details.

---

### done

Mark a task as completed.

```bash
scripts/reminders.sh done <task-name>
```

**Arguments:**
- `<task-name>` (required) - Exact title of the task to complete

**Behavior:** Searches across all lists for the first matching incomplete task and marks it completed.

**Output:** Confirmation message or error if task not found.

---

### edit

Modify an existing task's properties.

```bash
scripts/reminders.sh edit <identifier> [options]
```

**Arguments:**
- `<identifier>` (required) - Task identifier (UUID or exact title)

**Options:**
- `--new-title <text>` - Update task title
- `--move-to-list <name>` - Move task to another list (by list name)
- `--notes <text>` - Update notes/description
- `--due <date>` - Update due date (formats: YYYY-MM-DD, today, tomorrow, next week)
- `--time <time>` - Update due time (format: HH:MM, e.g., "14:00")
- `--priority <level>` - Update priority (high/medium/low/none)
- `--url <url>` - Update associated URL
- `--flagged` - Mark as flagged
- `--unflagged` - Remove flagged status

**Behavior:** Finds task by UUID (preferred) or exact title match, then updates specified properties.

**Output:** Confirmation message with updated task details or error if task not found.

**Examples:**
```bash
# Update task due date
scripts/reminders.sh edit "Review PR" --due "2026-01-20"

# Move task to another list
scripts/reminders.sh edit "找一下博士offer" --move-to-list "生活"

# Update multiple properties at once
scripts/reminders.sh edit "Review PR" --due tomorrow --priority high --flagged
```

---

### delete

Permanently remove a task.

```bash
scripts/reminders.sh delete <identifier>
```

**Arguments:**
- `<identifier>` (required) - Task identifier (UUID or exact title)

**Behavior:** Finds task by UUID (preferred) or exact title match, then removes it from the system.

**Output:** Confirmation message or error if task not found.

**Warning:** This operation is irreversible. The task will be permanently deleted, not just marked as completed.

---

### search

Search for tasks by keyword.

```bash
scripts/reminders.sh search <keyword>
```

**Arguments:**
- `<keyword>` (required) - Search term (case-insensitive)

**Behavior:** Searches task titles across all lists.

**Output:** Markdown-formatted list of matching tasks.

---

## Implementation Details

**Technology Stack:**
- **Swift + EventKit**: All CRUD operations (list/add/edit/delete/done/search) use native macOS EventKit framework
- **Bash**: Command routing, argument parsing, output formatting
- **Hybrid Architecture**: Flagged property uses AppleScript bridge (EventKit API limitation)

**Key Features:**
- Native macOS integration through EventKit
- Complete CRUD support with rich metadata (priority, due date+time, notes, URL, flagged)
- Support for nested lists (groups)
- UUID-based task identification for reliable updates/deletes
- Instant compilation (no pre-built binaries)
- Markdown-formatted output optimized for Claude conversations

**Display Enhancements:**
- 🚩 Flagged indicator for important tasks
- 🔗 URL indicator for tasks with links
- ⏰ Time display for tasks with specific due times
- JSON data flow for extensibility
