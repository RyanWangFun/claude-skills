-- list_notes.applescript
-- 列出指定文件夹下的所有笔记，输出 JSON 格式
-- 参数: folder_name

on run argv
    if (count of argv) < 1 then
        return "ERROR: Missing folder name argument"
    end if

    set folderName to item 1 of argv

    tell application "Notes"
        try
            set targetFolder to folder folderName
        on error
            return "ERROR: Folder not found: " & folderName
        end try

        set allNotes to every note of targetFolder
        set jsonParts to {}

        repeat with n in allNotes
            set nName to name of n
            set nId to id of n
            set nCreated to creation date of n as string
            set nModified to modification date of n as string

            -- 转义 JSON 字符串
            set nNameEscaped to my escapeJSON(nName)

            set jsonPart to "{\"id\": \"" & nId & "\", \"name\": \"" & nNameEscaped & "\", \"created\": \"" & nCreated & "\", \"modified\": \"" & nModified & "\"}"
            set end of jsonParts to jsonPart
        end repeat

        -- 构建 JSON 数组
        set jsonString to "["
        set firstPart to true
        repeat with part in jsonParts
            if firstPart is false then
                set jsonString to jsonString & ", "
            end if
            set jsonString to jsonString & part
            set firstPart to false
        end repeat
        set jsonString to jsonString & "]"

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
