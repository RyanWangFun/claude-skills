# Reminders Usage Examples

## Basic Task Management

### Viewing Tasks

```bash
# List all tasks
scripts/reminders.sh list

# List tasks from a specific list
scripts/reminders.sh list "Work"
scripts/reminders.sh list "01Projects"
```

### Creating Simple Tasks

```bash
# Add to default list
scripts/reminders.sh add "Review code"

# Add to specific list
scripts/reminders.sh add "Call dentist" --list "Personal"
```

### Completing Tasks

```bash
scripts/reminders.sh done "Review code"
scripts/reminders.sh done "Call dentist"
```

## List Management

### Creating and Organizing Lists

```bash
# Create a new project list
scripts/reminders.sh create-list "Project X" --color "#FF0000"

# View all lists
scripts/reminders.sh list-lists

# Rename a list
scripts/reminders.sh rename-list "Project X" "Project X - Phase 1"

# Delete a completed project list
scripts/reminders.sh delete-list "Old Project"
```

### Moving Tasks 

```bash
# Move a task to another list
scripts/reminders.sh edit "Review docs" --move-to-list "Project X"
```

## Advanced Task Creation

### With Due Dates

```bash
# Using natural language
scripts/reminders.sh add "Submit report" --due tomorrow
scripts/reminders.sh add "Team meeting prep" --due "next week"

# Using specific dates
scripts/reminders.sh add "File taxes" --due "2026-04-15"
```

### With Priorities

```bash
scripts/reminders.sh add "Fix critical bug" --priority high
scripts/reminders.sh add "Update docs" --priority low
scripts/reminders.sh add "Review PR" --priority medium
```

### With URLs and Flags

```bash
# Add task with URL reference
scripts/reminders.sh add "Review PR #456" \
  --list "Work" \
  --url "https://github.com/user/repo/pull/456" \
  --priority high

# Add flagged task for high visibility
scripts/reminders.sh add "Urgent: Security patch" \
  --flagged \
  --priority high \
  --due today
```

### With Specific Time

```bash
# Task with date and time
scripts/reminders.sh add "Team standup" \
  --due today \
  --time "09:30" \
  --list "Work"

# Meeting reminder
scripts/reminders.sh add "Client call" \
  --due tomorrow \
  --time "14:00" \
  --notes "Discuss Q1 roadmap"
```

### Complete Task with All Options

```bash
scripts/reminders.sh add "Complete API documentation" \
  --list "Work" \
  --notes "Include authentication endpoints and error codes" \
  --due "2026-01-20" \
  --time "17:00" \
  --priority high \
  --url "https://docs.example.com" \
  --flagged
```

## Search Operations

```bash
# Find tasks containing keyword
scripts/reminders.sh search "meeting"
scripts/reminders.sh search "review"
scripts/reminders.sh search "urgent"
```

## Editing Tasks

### Changing Task Properties

```bash
# Update due date
scripts/reminders.sh edit "Review PR" --due "2026-01-25"

# Add or update notes
scripts/reminders.sh edit "Team meeting" --notes "Agenda: Q1 planning, budget review"

# Change priority
scripts/reminders.sh edit "Documentation update" --priority high

# Update time
scripts/reminders.sh edit "Client call" --time "15:00"
```

### Flagging and Unflagging

```bash
# Mark as important
scripts/reminders.sh edit "Security audit" --flagged

# Remove flag
scripts/reminders.sh edit "Old urgent task" --unflagged
```

### Renaming Tasks

```bash
# Update task title
scripts/reminders.sh edit "Fix bug" --new-title "Fix authentication bug in login flow"
```

### Multiple Property Updates

```bash
# Update several properties at once
scripts/reminders.sh edit "API Implementation" \
  --new-title "REST API Implementation - Phase 1" \
  --due "2026-02-15" \
  --time "18:00" \
  --priority high \
  --notes "Focus on authentication endpoints first" \
  --flagged
```

## Deleting Tasks

```bash
# Delete by exact title
scripts/reminders.sh delete "Obsolete task"

# Delete using UUID (more reliable for tasks with duplicate names)
scripts/reminders.sh delete "A1B2C3D4-1234-5678-90AB-CDEF12345678"
```

## Common Workflows

### Project Task Creation

```bash
# Add task to project-specific list with context
scripts/reminders.sh add "Implement user authentication" \
  --list "MyApp Project" \
  --notes "Use OAuth2 with JWT tokens. See design doc in Notion." \
  --due "2026-01-25" \
  --priority high
```

### Daily Planning

```bash
# Check what's on my plate
scripts/reminders.sh list

# Add today's priority tasks
scripts/reminders.sh add "Morning standup" --due today --priority high
scripts/reminders.sh add "Code review for PR #123" --due today

# Complete tasks as you go
scripts/reminders.sh done "Morning standup"
```

### Context-Driven Task Management

```bash
# When working on a specific project
scripts/reminders.sh list "01Projects"

# Add task related to current context
scripts/reminders.sh add "Update CLAUDE.md with new patterns" \
  --list "01Projects" \
  --notes "Document the Progressive Disclosure pattern"

# Search for related tasks
scripts/reminders.sh search "documentation"
```

### Task Refinement Workflow

```bash
# Create initial task quickly
scripts/reminders.sh add "Fix login issue"

# After investigation, refine with details
scripts/reminders.sh edit "Fix login issue" \
  --new-title "Fix OAuth token expiration in login flow" \
  --notes "Token refresh fails after 1 hour. Check refresh_token endpoint." \
  --url "https://github.com/company/app/issues/789" \
  --priority high \
  --due tomorrow \
  --flagged
```

### Deadline Management

```bash
# List all tasks to review deadlines
scripts/reminders.sh list

# Postpone a task
scripts/reminders.sh edit "Quarterly report" --due "next week"

# Add time to existing deadline
scripts/reminders.sh edit "Client presentation" --time "10:00"

# Mark urgent tasks
scripts/reminders.sh edit "Budget approval" --flagged --priority high
```

### Cleanup and Maintenance

```bash
# Search for old tasks
scripts/reminders.sh search "2025"

# Delete obsolete tasks
scripts/reminders.sh delete "Old project planning"
scripts/reminders.sh delete "Deprecated feature implementation"

# Or mark as done if you want history
scripts/reminders.sh done "Completed but not marked"
```

## Integration with Claude Conversations

In Claude Code, you can use natural language:

**User:** "Show me my work tasks"
**Claude:** Executes `scripts/reminders.sh list "Work"`

**User:** "Add a reminder to review the PR tomorrow at 2pm"
**Claude:** Executes `scripts/reminders.sh add "Review PR" --due tomorrow --time "14:00" --list "Work"`

**User:** "Make that task high priority and flag it"
**Claude:** Executes `scripts/reminders.sh edit "Review PR" --priority high --flagged`

**User:** "Change the deadline to next Monday"
**Claude:** Executes `scripts/reminders.sh edit "Review PR" --due "2026-01-20"`

**User:** "Mark the standup task as done"
**Claude:** Executes `scripts/reminders.sh done "Morning standup"`

**User:** "Delete the old planning task"
**Claude:** Executes `scripts/reminders.sh delete "old planning task"`
