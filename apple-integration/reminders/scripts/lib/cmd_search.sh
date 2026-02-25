#!/bin/bash

# Search Command Logic

KEYWORD="${1:-}"

if [[ -z "$KEYWORD" ]]; then
    error_exit "Search keyword is required. Usage: ... search <keyword>"
fi

KEYWORD_ESCAPED="${KEYWORD//\"/\\\"}"

echo ""
echo "🔍 Searching for: $KEYWORD"
echo ""

# Search across all lists with UNFILTERED BULK FETCH
SEARCH_RESULTS=$(osascript -e "tell application \"Reminders\"
    set output to \"\"
    set allLists to every list
    repeat with aList in allLists
        set listName to name of aList
        try
            set rList to every reminder of aList
            set rCount to count of rList
            if rCount > 0 then
                set rNames to (name of every reminder of aList) as list
                set rBodies to (body of every reminder of aList) as list
                set rCompleted to (completed of every reminder of aList) as list
                set rPriorities to (priority of every reminder of aList) as list
                set rDueDates to (due date of every reminder of aList) as list

                repeat with i from 1 to rCount
                    if item i of rCompleted is false then
                        set taskName to item i of rNames
                        set taskBody to item i of rBodies
                        
                        -- Search in name or body
                        if taskName contains \"$KEYWORD_ESCAPED\" or taskBody contains \"$KEYWORD_ESCAPED\" then
                            set taskPriority to item i of rPriorities
                            set taskDue to item i of rDueDates
                            set output to output & listName & \"||\" & taskName & \"||\" & taskBody & \"||\" & taskPriority & \"||\" & taskDue & \"\\n\"
                        end if
                    end if
                end repeat
            end if
        on error
            -- Skip lists that fail
        end try
    end repeat
    return output
end tell" 2>&1)

if [[ -z "$SEARCH_RESULTS" ]]; then
    echo "*No tasks found matching '$KEYWORD'*"
else
    current_list=""
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            IFS='||' read -r list_name name body priority due <<< "$line"

            # Print list header if changed
            if [[ "$list_name" != "$current_list" ]]; then
                if [[ -n "$current_list" ]]; then
                    echo ""
                fi
                echo "## $list_name"
                echo ""
                current_list="$list_name"
            fi

            task_line="- [ ] $name"

            priority_badge=$(format_priority "$priority")
            if [[ -n "$priority_badge" ]]; then
                task_line="$task_line $priority_badge"
            fi

            if [[ "$due" != "missing value" ]]; then
                date_badge=$(format_date "$due")
                if [[ -n "$date_badge" ]]; then
                    task_line="$task_line $date_badge"
                fi
            fi

            echo "$task_line"

            if [[ "$body" != "missing value" && -n "$body" ]]; then
                echo "      💭 $body"
            fi
        fi
    done <<< "$SEARCH_RESULTS"
fi
echo ""
