-- list_folders.applescript
-- 列出所有文件夹，输出 JSON 格式

tell application "Notes"
    set allFolders to every folder
    set jsonParts to {}

    repeat with f in allFolders
        set fName to name of f
        set fId to id of f
        set noteCount to count of notes of f

        -- 转义 JSON 字符串
        set fNameEscaped to my escapeJSON(fName)

        set jsonPart to "{\"id\": \"" & fId & "\", \"name\": \"" & fNameEscaped & "\", \"count\": " & noteCount & "}"
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
