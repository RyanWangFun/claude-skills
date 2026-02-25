import EventKit
import Foundation

// MARK: - Data Structures

struct ReminderItem: Codable {
    let id: String
    let title: String
    let notes: String?
    let url: String?
    let priority: Int
    let isCompleted: Bool
    let dueDate: String?
    let hasTime: Bool
    let list: String
    let isFlagged: Bool
}

struct FilterOptions {
    var listName: String?
    var dueDate: String?    // "today", "tomorrow", "this-week", "overdue"
    var priority: String?   // "high", "medium", "low"
    var flagged: Bool
}

// MARK: - Helpers

func logError(_ message: String) {
    fputs("Error: \(message)\n", stderr)
}

func parseArgs() -> FilterOptions {
    var options = FilterOptions(listName: nil, dueDate: nil, priority: nil, flagged: false)
    let args = CommandLine.arguments
    
    var i = 1
    while i < args.count {
        let arg = args[i]
        
        switch arg {
        case "--list", "-l":
            if i + 1 < args.count {
                options.listName = args[i + 1]
                i += 1
            }
        case "--due":
            if i + 1 < args.count {
                options.dueDate = args[i + 1]
                i += 1
            }
        case "--priority":
            if i + 1 < args.count {
                options.priority = args[i + 1]
                i += 1
            }
        case "--flagged":
            options.flagged = true
        default:
            // Support positional list name for backward compatibility if it's the first arg and not a flag
            if i == 1 && !arg.hasPrefix("-") {
                options.listName = arg
            }
        }
        i += 1
    }
    return options
}

func getDateRange(for keyword: String) -> (start: Date?, end: Date?)? {
    let calendar = Calendar.current
    let now = Date()
    let startOfDay = calendar.startOfDay(for: now)
    
    switch keyword.lowercased() {
    case "today":
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!
        return (startOfDay, endOfDay)
        
    case "tomorrow":
        let startOfTomorrow = calendar.date(byAdding: .day, value: 1, to: startOfDay)!
        let endOfTomorrow = calendar.date(byAdding: .day, value: 1, to: startOfTomorrow)!
        return (startOfTomorrow, endOfTomorrow)
        
    case "this-week":
        // Until end of next Sunday? Or just next 7 days? 
        // Let's assume standard "This Week" (until upcoming Sunday or +7 days)
        // For simplicity: Today + 7 days
        let endOfWeek = calendar.date(byAdding: .day, value: 7, to: startOfDay)!
        return (startOfDay, endOfWeek)
        
    case "overdue":
        // Completed is false, and date < now
        return (nil,  now)
        
    default:
        // Try parsing YYYY-MM-DD
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFullDate]
        if let date = formatter.date(from: keyword) {
            let nextDay = calendar.date(byAdding: .day, value: 1, to: date)!
            return (date, nextDay)
        }
        return nil
    }
}

// Helper to fetch flagged IDs via AppleScript
// Note: When querying ALL lists, this is expensive.
// We might optimize by only using it when specifically filtering by flagged or for a specific list.
func fetchFlaggedIds(listName: String?) -> Set<String> {
    var script = ""
    if let name = listName {
        script = "tell application \"Reminders\" to get id of (reminders in list \"\(name)\" whose flagged is true)"
    } else {
        // Querying all lists via AppleScript is slow and tricky.
        // Optimization: For "All Lists", we might skip this for now or iterate lists logic in Swift if we can't find property.
        // Actually, EKReminder doesn't expose 'flagged' in older OS versions directly, but modern ones do?
        // Wait, EKReminder DOES NOT have 'isFlagged' property exposed easily in public API until very recently or never?
        // Checking API: EKReminder has no 'flagged' property. It uses 'priority' sometimes? No.
        // It's a known limitation. We must use AppleScript or private API.
        // For "All Lists", let's try a better AppleScript that iterates all lists efficiently?
        // Or just `get id of (reminders whose flagged is true)` - might simpler?
        // "reminders" object exists at application level? usually just lists.
        script = "tell application \"Reminders\" to get id of (reminders of lists whose flagged is true)"
        // The above AppleScript syntax might be wrong for flattening.
        // Let's stick to safe approach: If listName is nil, we iterate all lists names we know? 
        // Or finding a way to get all flagged items.
        // Simplified apporach:
        script = """
        tell application "Reminders"
            set all_ids to {}
            repeat with l in lists
                set list_ids to id of (reminders in l whose flagged is true)
                set all_ids to all_ids & list_ids
            end repeat
            return all_ids
        end tell
        """
    }
    
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    process.arguments = ["-e", script]
    
    let pipe = Pipe()
    process.standardOutput = pipe
    
    do {
        try process.run()
        process.waitUntilExit()
        
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        if let output = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) {
            if output.isEmpty || output == "{}" { return [] }
            
            // Clean up AppleScript list output format "id1, id2" or "{id1, id2}"
            let cleaned = output.replacingOccurrences(of: "{", with: "")
                                .replacingOccurrences(of: "}", with: "")
            
            let rawIds = cleaned.components(separatedBy: ",")
            var uuidSet = Set<String>()
            
            for rawId in rawIds {
                let trimmed = rawId.trimmingCharacters(in: .whitespaces)
                if trimmed.isEmpty { continue }
                
                let prefix = "x-apple-reminder://"
                if trimmed.hasPrefix(prefix) {
                    let uuid = String(trimmed.dropFirst(prefix.count))
                    uuidSet.insert(uuid)
                } else {
                    uuidSet.insert(trimmed)
                }
            }
            return uuidSet
        }
    } catch {
        // Fallback or error
    }
    return []
}


// MARK: - Main Logic

let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)
let options = parseArgs()

func main() {
    // Determine Calendars
    let calendars = store.calendars(for: .reminder)
    var targetCalendars: [EKCalendar] = []
    
    if let name = options.listName {
        targetCalendars = calendars.filter { $0.title == name }
        if targetCalendars.isEmpty {
            logError("List '\(name)' not found")
            exit(1)
        }
    } else {
        // All lists
        targetCalendars = calendars
    }
    
    // Build Predicate
    var predicate: NSPredicate?
    
    if let dueKeyword = options.dueDate, let range = getDateRange(for: dueKeyword) {
        if dueKeyword == "overdue" {
             predicate = store.predicateForIncompleteReminders(withDueDateStarting: nil, ending: range.end, calendars: targetCalendars)
        } else {
            // Range
            predicate = store.predicateForIncompleteReminders(withDueDateStarting: range.start, ending: range.end, calendars: targetCalendars)
        }
    } else {
        // No date filter, match all incomplete
        predicate = store.predicateForReminders(in: targetCalendars)
    }
    
    guard let searchPredicate = predicate else {
        print("[]")
        return
    }
    
    // Fetch Flagged IDs if needed (or always to show status)
    // We always fetch them to populate 'isFlagged' property correctly
    // Optimization: If options.flagged is true, we ONLY care about these IDs.
    let flaggedIds = fetchFlaggedIds(listName: options.listName)
    
    store.fetchReminders(matching: searchPredicate) { reminders in
        guard let reminders = reminders else {
            print("[]")
            semaphore.signal()
            return
        }
        
        var outputItems: [ReminderItem] = []
        let formatter = ISO8601DateFormatter()
        
        for reminder in reminders {
            // Basic Completion Filter
            if reminder.isCompleted { continue }
            
            // Priority Filter
            // EKPriority: 1-4 High, 5 Medium, 6-9 Low, 0 None
            if let pFilter = options.priority {
                let p = reminder.priority
                var match = false
                switch pFilter.lowercased() {
                case "high": match = (p >= 1 && p <= 4)
                case "medium": match = (p == 5)
                case "low": match = (p >= 6 && p <= 9)
                case "none": match = (p == 0)
                default: match = true
                }
                if !match { continue }
            }
            
            // Flagged Filter
            // Note: Since we fetched flagged IDs, we check if this ID is in the set.
            let isFlagged = flaggedIds.contains(reminder.calendarItemIdentifier)
            if options.flagged && !isFlagged {
                continue
            }
            
            // Due Date Filter Additional Check (for "Overdue")
            // Predicate "ending at now" includes anything due before now.
            // But we might want to exclude things that have no due date?
            // "overdue" implies it HAS a due date and it is passed.
            if options.dueDate == "overdue" {
                 if reminder.dueDateComponents == nil { continue }
            }
            
            // Serialize
            let id = reminder.calendarItemIdentifier
            let title = reminder.title ?? "Untitled"
            let notes = reminder.notes
            let urlStr = reminder.url?.absoluteString
            let priority = reminder.priority
            
            var dueStr: String? = nil
            var hasTime = false

            if let dueComponents = reminder.dueDateComponents {
                // Check if has time component
                if dueComponents.hour != nil && dueComponents.minute != nil {
                    hasTime = true
                    // Has time: use full ISO8601 format with timezone
                    if let date = Calendar.current.date(from: dueComponents) {
                        dueStr = formatter.string(from: date)
                    }
                } else {
                    // No time: format date only to avoid timezone conversion issues
                    if let year = dueComponents.year,
                       let month = dueComponents.month,
                       let day = dueComponents.day {
                        dueStr = String(format: "%04d-%02d-%02d", year, month, day)
                    }
                }
            }
            
            let listName = reminder.calendar.title
            
            let item = ReminderItem(
                id: id,
                title: title,
                notes: notes,
                url: urlStr,
                priority: priority,
                isCompleted: reminder.isCompleted,
                dueDate: dueStr,
                hasTime: hasTime,
                list: listName, // Include list name for grouping
                isFlagged: isFlagged
            )
            
            outputItems.append(item)
        }
        
        // Output JSON
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        
        do {
            let jsonData = try encoder.encode(outputItems)
            if let jsonString = String(data: jsonData, encoding: .utf8) {
                print(jsonString)
            }
        } catch {
            logError("Failed to encode JSON: \(error)")
            exit(1)
        }
        
        semaphore.signal()
    }
}

// Request Access
if #available(macOS 14.0, *) {
    store.requestFullAccessToReminders { (granted, error) in
        if granted {
            main()
        } else {
            logError("Access denied: \(String(describing: error))")
            exit(1)
        }
    }
} else {
    store.requestAccess(to: .reminder) { (granted, error) in
        if granted {
            main()
        } else {
            logError("Access denied: \(String(describing: error))")
            exit(1)
        }
    }
}

semaphore.wait()
