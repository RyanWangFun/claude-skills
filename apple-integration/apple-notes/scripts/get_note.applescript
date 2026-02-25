-- get_note.applescript
-- 获取指定笔记的完整内容，输出 JSON 格式
-- 参数: note_id 或 folder_name note_name

on run argv
    if (count of argv) < 1 then
        return "ERROR: Missing arguments. Usage: get_note <note_id> or get_note <folder_name> <note_name>"
    end if

    tell application "Notes"
        set targetNote to missing value

        if (count of argv) = 1 then
            -- 通过 ID 查找
            set noteId to item 1 of argv
            try
                set targetNote to first note whose id is noteId
            on error
                return "ERROR: Note not found with ID: " & noteId
            end try
        else
            -- 通过文件夹名和笔记名查找
            set folderName to item 1 of argv
            set noteName to item 2 of argv
            try
                set targetFolder to folder folderName
                set targetNote to first note of targetFolder whose name is noteName
            on error
                return "ERROR: Note not found: " & noteName & " in folder: " & folderName
            end try
        end if

        if targetNote is missing value then
            return "ERROR: Note not found"
        end if

        set nName to name of targetNote
        set nId to id of targetNote
        set nBody to body of targetNote
        set nCreated to creation date of targetNote as string
        set nModified to modification date of targetNote as string

        -- 转义 JSON 字符串
        set nNameEscaped to my escapeJSON(nName)
        set nBodyEscaped to my escapeJSON(nBody)

        set jsonString to "{\"id\": \"" & nId & "\", \"name\": \"" & nNameEscaped & "\", \"body\": \"" & nBodyEscaped & "\", \"created\": \"" & nCreated & "\", \"modified\": \"" & nModified & "\"}"

        return jsonString
    end tell
end run

on escapeJSON(str)
    try
        set text item delimiters to "\\"
        set str to text items of str
        set text item delimiters to "\\\\"
        set str to str as text

        set text item delimiters to "\""
        set str to text items of str
        set text item delimiters to "\\\""
        set str to str as text

        set text item delimiters to return
        set str to text items of str
        set text item delimiters to "\\n"
        set str to str as text

        set text item delimiters to linefeed
        set str to text items of str
        set text item delimiters to "\\n"
        set str to str as text
    on error
        return ""
    end try
    return str
end escapeJSON
