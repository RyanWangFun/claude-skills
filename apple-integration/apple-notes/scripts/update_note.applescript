-- update_note.applescript
-- 更新笔记内容
-- 参数: note_id, new_body 或 folder_name, note_name, new_body

on run argv
    if (count of argv) < 2 then
        return "ERROR: Missing arguments. Usage: update_note <note_id> <new_body> or update_note <folder> <note_name> <new_body>"
    end if

    tell application "Notes"
        set targetNote to missing value

        if (count of argv) = 2 then
            -- 通过 ID 更新
            set noteId to item 1 of argv
            set newBody to item 2 of argv
            try
                set targetNote to first note whose id is noteId
            on error
                return "ERROR: Note not found with ID: " & noteId
            end try
        else if (count of argv) >= 3 then
            -- 通过文件夹名和笔记名更新
            set folderName to item 1 of argv
            set noteName to item 2 of argv
            set newBody to item 3 of argv
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

        -- 转换文本为 HTML（如果需要）
        if newBody does not contain "<" then
            -- 保留原标题
            set noteTitle to name of targetNote
            set htmlBody to "<h1>" & noteTitle & "</h1><br>" & my textToHtml(newBody)
        else
            set htmlBody to newBody
        end if

        set body of targetNote to htmlBody

        return id of targetNote
    end tell
end run

on textToHtml(txt)
    set text item delimiters to linefeed
    set txtParts to text items of txt
    set text item delimiters to "<br>"
    set htmlTxt to txtParts as text

    set text item delimiters to return
    set txtParts to text items of htmlTxt
    set text item delimiters to "<br>"
    set htmlTxt to txtParts as text

    return htmlTxt
end textToHtml
