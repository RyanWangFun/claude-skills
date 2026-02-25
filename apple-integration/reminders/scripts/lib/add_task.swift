import EventKit
import Foundation

// Helper to write to stderr
func logError(_ message: String) {
    fputs("❌ Error: \(message)\n", stderr)
}

func logSuccess(_ message: String) {
    print(message)
}

// Argument definitions
var title: String?
var listName: String?
var notes: String?
var priority: Int = 0
var dueString: String?
var timeString: String?
var urlString: String?
var isFlagged: Bool = false

// Simple argument parsing
var args = CommandLine.arguments
args.removeFirst() // Remove binary name

while !args.isEmpty {
    let arg = args.removeFirst()
    switch arg {
    case "--list":
        guard !args.isEmpty else { logError("Missing value for --list"); exit(1) }
        listName = args.removeFirst()
    case "--notes":
        guard !args.isEmpty else { logError("Missing value for --notes"); exit(1) }
        notes = args.removeFirst()
    case "--priority":
        guard !args.isEmpty else { logError("Missing value for --priority"); exit(1) }
        if let p = Int(args.removeFirst()) {
            priority = p
        }
    case "--due":
        guard !args.isEmpty else { logError("Missing value for --due"); exit(1) }
        dueString = args.removeFirst()
    case "--time":
        guard !args.isEmpty else { logError("Missing value for --time"); exit(1) }
        timeString = args.removeFirst()
    case "--url":
        guard !args.isEmpty else { logError("Missing value for --url"); exit(1) }
        urlString = args.removeFirst()
    case "--flagged", "-f":
        isFlagged = true
    default:
        if title == nil {
            title = arg
        }
    }
}

guard let taskTitle = title else {
    logError("Title required")
    exit(1)
}

let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)

// Function to calculate due date components
func calculateDueDate(dateStr: String, timeStr: String?) -> DateComponents? {
    let lowerObj = dateStr.lowercased()
    let now = Date()
    var date: Date?
    
    if lowerObj == "today" {
        date = now
    } else if lowerObj == "tomorrow" {
        date = Calendar.current.date(byAdding: .day, value: 1, to: now)
    } else if lowerObj == "next week" || lowerObj == "nextweek" {
        date = Calendar.current.date(byAdding: .day, value: 7, to: now)
    } else {
        // Try YYYY-MM-DD
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        date = formatter.date(from: dateStr)
    }
    
    guard let resolvedDate = date else { return nil }
    
    var components = Calendar.current.dateComponents([.year, .month, .day], from: resolvedDate)
    
    // Add time if provided
    if let t = timeStr {
        // Expected format HH:mm
        let parts = t.components(separatedBy: ":")
        if parts.count == 2, let h = Int(parts[0]), let m = Int(parts[1]) {
            components.hour = h
            components.minute = m
        }
    } else if lowerObj == "today" {
         // If today and no time, maybe set to end of day? 
         // Or leave as date only. Standard is date only implies "all day" task in some views, 
         // or specific time default. Let's keep date only if no time specified.
    }
    
    return components
}

func setFlagged(reminderId: String) {
    // Robust script to handle "x-apple-reminder://" prefix or raw ID
    let script = """
    tell application "Reminders"
        -- Try searching by full ID (usually x-apple-reminder://UUID)
        try
            set targetTask to (first reminder whose id is "x-apple-reminder://\(reminderId)")
            set flagged of targetTask to true
            return
        end try
        
        -- Try searching by raw UUID
        try
             set targetTask to (first reminder whose id is "\(reminderId)")
             set flagged of targetTask to true
             return
        end try
        
        -- Fallback: iterate (slow but safe, only for recently added top 1?) 
        -- Actually, ID lookups should work if we have the right string.
        -- Let's just log error if both fail.
    end tell
    """
    
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    process.arguments = ["-e", script]
    
    do {
        try process.run()
        process.waitUntilExit()
    } catch {
        fputs("⚠️ Warning: Failed to set flagged status\n", stderr)
    }
}

func performAdd() {
    // find list
    var calendar: EKCalendar?
    if let name = listName {
        let calendars = store.calendars(for: .reminder)
        calendar = calendars.first(where: { $0.title == name })
        if calendar == nil {
            logError("List '\(name)' not found")
            exit(1)
        }
    } else {
        calendar = store.defaultCalendarForNewReminders()
        if calendar == nil {
            logError("No default list found")
            exit(1)
        }
    }
    
    let reminder = EKReminder(eventStore: store)
    reminder.calendar = calendar!
    reminder.title = taskTitle
    reminder.notes = notes
    reminder.priority = priority
    
    // URL support
    if let uStr = urlString {
         if let u = URL(string: uStr) {
             reminder.url = u
         } else {
             logError("Invalid URL: \(uStr)")
         }
    }
    
    if let dueStr = dueString {
        if let comps = calculateDueDate(dateStr: dueStr, timeStr: timeString) {
            reminder.dueDateComponents = comps
        } else {
            logError("Invalid date format: \(dueStr). Use YYYY-MM-DD, 'today', 'tomorrow', or 'next week'")
            exit(1)
        }
    } else if let _ = timeString {
        // Time provided but no date? Assume today?
        // Let's require due date explicitly for clarity
        logError("--due required when specifying --time")
        exit(1)
    }
    
    do {
        try store.save(reminder, commit: true)
        
        if isFlagged {
            setFlagged(reminderId: reminder.calendarItemIdentifier)
        }
        
        logSuccess("✅ Added task '\(taskTitle)'")
        if isFlagged {
             // print("   (Flagged)")
        }
        semaphore.signal()
    } catch {
        logError("Failed to save reminder: \(error.localizedDescription)")
        exit(1)
    }
}

if #available(macOS 14.0, *) {
    store.requestFullAccessToReminders { (granted, error) in
        if granted {
            performAdd()
        } else {
            logError("Access denied: \(String(describing: error))")
            exit(1)
        }
    }
} else {
    store.requestAccess(to: .reminder) { (granted, error) in
        if granted {
            performAdd()
        } else {
            logError("Access denied: \(String(describing: error))")
            exit(1)
        }
    }
}

semaphore.wait()
