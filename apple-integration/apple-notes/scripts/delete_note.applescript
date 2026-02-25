-- delete_note.applescript
-- 删除笔记
-- 参数: note_id 或 folder_name note_name

on run argv
    if (count of argv) < 1 then
        return "ERROR: Missing arguments. Usage: delete_note <note_id> or delete_note <folder> <note_name>"
    end if

    tell application "Notes"
        set targetNote to missing value

        if (count of argv) = 1 then
            -- 通过 ID 删除
            set noteId to item 1 of argv
            try
                set targetNote to first note whose id is noteId
            on error
                return "ERROR: Note not found with ID: " & noteId
            end try
        else
            -- 通过文件夹名和笔记名删除
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

        set noteId to id of targetNote
        delete targetNote

        return "DELETED:" & noteId
    end tell
end run
