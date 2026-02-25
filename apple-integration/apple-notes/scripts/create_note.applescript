-- create_note.applescript
-- 在指定文件夹创建新笔记
-- 参数: folder_name, title, [body]

on run argv
    if (count of argv) < 2 then
        return "ERROR: Missing arguments. Usage: create_note <folder_name> <title> [body]"
    end if

    set folderName to item 1 of argv
    set noteTitle to item 2 of argv
    set noteBody to ""
    if (count of argv) > 2 then
        set noteBody to item 3 of argv
    end if

    tell application "Notes"
        try
            set targetFolder to folder folderName
        on error
            return "ERROR: Folder not found: " & folderName
        end try

        -- 创建笔记，body 需要是 HTML 格式
        -- 如果 body 不包含 HTML 标签，包装成简单的 HTML
        if noteBody is "" then
            set htmlBody to "<h1>" & noteTitle & "</h1>"
        else
            -- 检查是否已经是 HTML
            if noteBody does not contain "<" then
                -- 纯文本，转换为 HTML
                set htmlBody to "<h1>" & noteTitle & "</h1><br>" & my textToHtml(noteBody)
            else
                set htmlBody to noteBody
            end if
        end if

        set newNote to make new note at targetFolder with properties {body:htmlBody}
        set newNoteId to id of newNote

        return newNoteId
    end tell
end run

on textToHtml(txt)
    -- 简单的文本转 HTML：换行符转 <br>
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
