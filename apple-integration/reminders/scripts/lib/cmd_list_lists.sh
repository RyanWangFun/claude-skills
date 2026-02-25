
# Execute Swift script to get JSON data
JSON_OUTPUT=$(swift "$SCRIPT_DIR/list_calendars.swift" 2>/dev/null)

if [ $? -ne 0 ]; then
    error_exit "Failed to fetch calendar lists."
fi

# Use Python to parse JSON and output Markdown table
python3 -c "
import sys, json

try:
    data = json.loads(sys.argv[1])
    print('## Reminders Lists\n')
    print('| Name | Source | ID (last 8) | Color |')
    print('|---|---|---|---|')
    for item in data:
        name = item.get('title', 'N/A')
        source = item.get('source', 'N/A')
        cid = item.get('id', '')
        short_id = cid[-8:] if len(cid) >= 8 else cid
        color = item.get('color') or 'N/A'
        print(f'| {name} | {source} | {short_id} | {color} |')
    print(f'\nTotal: {len(data)} lists')
except Exception as e:
    print(f'Error processing data: {e}')
    sys.exit(1)
" "$JSON_OUTPUT"
