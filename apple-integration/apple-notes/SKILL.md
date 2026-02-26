---
name: apple-notes
description: |
  Control macOS Notes.app through natural language. Full CRUD operations: list folders, list/read/create/update/delete notes, with HTML table support. Use when user wants to:
  (1) View or search notes/folders ("查看备忘录", "看看笔记", "list notes")
  (2) Create notes ("记录到备忘录", "创建笔记", "add to notes")
  (3) Update notes ("更新备忘录", "修改笔记", "update note")
  (4) Delete notes ("删除笔记", "remove note")
  (5) Manage shared lists like grocery/fridge inventory ("冰箱清单", "购物清单", "shopping list")
  Supports HTML tables for structured data. Notes can be shared via iCloud.
---

# Apple Notes

Control macOS Notes.app with full CRUD operations and table support.

## Quick Reference

| Action | Script | Example |
|--------|--------|---------|
| List folders | `list_folders.applescript` | `osascript scripts/list_folders.applescript` |
| List notes | `list_notes.applescript` | `osascript scripts/list_notes.applescript "Notes"` |
| Read note | `get_note.applescript` | `osascript scripts/get_note.applescript "Notes" "笔记名"` |
| Create note | `create_note.applescript` | `osascript scripts/create_note.applescript "Notes" "标题" "内容"` |
| Update note | `update_note.applescript` | `osascript scripts/update_note.applescript "Notes" "笔记名" "新内容"` |
| Delete note | `delete_note.applescript` | `osascript scripts/delete_note.applescript "Notes" "笔记名"` |

## Scripts

Located in `scripts/` relative to this SKILL.md. Run with `osascript`:

```bash
# Get skill directory
SKILL_DIR="$SKILLS_DIR/apple-notes"

# List all folders
osascript "$SKILL_DIR/scripts/list_folders.applescript"

# List notes in folder
osascript "$SKILL_DIR/scripts/list_notes.applescript" "Notes"

# Get note content (by folder + name)
osascript "$SKILL_DIR/scripts/get_note.applescript" "Notes" "笔记名"

# Get note content (by ID)
osascript "$SKILL_DIR/scripts/get_note.applescript" "x-coredata://..."

# Create note
osascript "$SKILL_DIR/scripts/create_note.applescript" "Notes" "标题" "内容"

# Update note
osascript "$SKILL_DIR/scripts/update_note.applescript" "Notes" "笔记名" "新内容"

# Delete note
osascript "$SKILL_DIR/scripts/delete_note.applescript" "Notes" "笔记名"
```

## Creating Tables

Notes.app supports HTML tables. Create structured data like inventories:

```bash
osascript -e '
tell application "Notes"
    set htmlBody to "<h1>冰箱清单</h1>
<table border=\"1\" style=\"border-collapse: collapse;\">
<tr style=\"background:#f0f0f0;\"><th>物品</th><th>数量</th><th>备注</th></tr>
<tr><td>牛奶</td><td>2</td><td>周五过期</td></tr>
<tr><td>鸡蛋</td><td>12</td><td></td></tr>
<tr><td>酸奶</td><td>3</td><td>草莓味</td></tr>
</table>"
    make new note at folder "Notes" with properties {body:htmlBody}
end tell
'
```

## Natural Language Mapping

| User says | Action |
|-----------|--------|
| 查看/列出文件夹 | `list_folders.applescript` |
| 看看 X 文件夹 | `list_notes.applescript "X"` |
| 读取/查看笔记 Y | `get_note.applescript "folder" "Y"` |
| 创建/添加/记录笔记 | `create_note.applescript` |
| 更新/修改笔记 | `update_note.applescript` |
| 删除笔记 | `delete_note.applescript` |
| 创建表格/清单 | Use HTML table format |

## Notes

- Default folder: "Notes" (中文系统可能显示为其他名称)
- Content format: HTML (支持 `<table>`, `<h1>`, `<div>`, `<br>`)
- Notes can be shared via iCloud for collaboration
- All scripts return JSON format for easy parsing
