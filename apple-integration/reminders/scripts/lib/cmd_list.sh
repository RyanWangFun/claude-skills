#!/bin/bash

# List Command Logic
# Usage: source cmd_list.sh [args...]

# Pass all arguments directly to get_tasks.swift
# logic is now handled in Swift (filtering, all lists, etc)

# robustly find the directory of this script (lib directory)
LIB_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GET_TASKS_BIN="$LIB_DIR/get_tasks"

# Ensure binary exists or fallback to swift run
if [[ ! -f "$GET_TASKS_BIN" ]]; then
    if [[ -f "$LIB_DIR/get_tasks.swift" ]]; then
        GET_TASKS_CMD="swift $LIB_DIR/get_tasks.swift"
    else
        echo "Error: get_tasks binary or script not found." >&2
        return 1
    fi
else
    GET_TASKS_CMD="$GET_TASKS_BIN"
fi

# Execute Swift script with all arguments
# Result is JSON array of tasks
JSON_OUTPUT=$($GET_TASKS_CMD "$@")

if [[ $? -ne 0 ]]; then
    echo "Error fetching tasks: $JSON_OUTPUT" >&2
    return 1
fi

# Use python to parse and format
echo "$JSON_OUTPUT" | python3 -c "
import sys, json, datetime

def format_priority(p):
    # EventKit: 1-4 High, 5 Medium, 6-9 Low, 0 None
    if p == 0: return \"\"
    if p < 5: return \"🔴\"   # High
    if p == 5: return \"🟡\"   # Medium
    return \"🔵\"            # Low

def format_date(iso_str, has_time):
    if not iso_str: return \"\"
    try:
        # iso_str expected YYYY-MM-DDTHH:MM:SSZ
        dt_str = iso_str[:10]
        if has_time and len(iso_str) > 11:
            time_str = iso_str[11:16]
            return f\"🗓️ {dt_str} {time_str}\"
        return f\"🗓️ {dt_str}\"
    except:
        return iso_str

try:
    data = json.load(sys.stdin)
except ValueError:
    # If Swift printed debug info or error before JSON, this might fail
    # But for now assume clean output
    sys.exit(0)

if not data:
    print(\"*No tasks found matching criteria*\")
else:
    # Sort by list name then by ID or title to group them
    # Actually, sorting by list name is enough for grouping
    data.sort(key=lambda x: x.get('list', ''))
    
    current_list = None
    
    for task in data:
        list_name = task.get('list', 'Unknown List')
        
        # Print List Header if changed
        if list_name != current_list:
            print(f\"\\n## {list_name}\")
            current_list = list_name
            
        flag = \"🚩 \" if task.get(\"isFlagged\", False) else \"\"
        p_badge = format_priority(task.get(\"priority\", 0))
        d_badge = format_date(task.get(\"dueDate\"), task.get(\"hasTime\", False))
        
        # Build line
        line = f\"- [ ] {flag}{task['title']}\"
        if p_badge: line += f\" {p_badge}\"
        if d_badge: line += f\" {d_badge}\"
        
        print(line)
        
        notes = task.get(\"notes\")
        if notes:
            clean_notes = notes.replace(\"\\n\", \"\\n      \")
            print(f\"      💭 {clean_notes}\")
            
        url = task.get(\"url\")
        if url:
            print(f\"      🔗 {url}\")
"
