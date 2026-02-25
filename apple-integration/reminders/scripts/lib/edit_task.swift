import EventKit
import Foundation

// Helper to write to stderr
func logError(_ message: String) {
    fputs("❌ Error: \(message)\n", stderr)
}

func logSuccess(_ message: String) {
    print(message)
}

// Arguments
var searchId: String?
var searchTitle: String?

// Update values
var newTitle: String?
var newNotes: String?
var newPriority: Int?
var newUrlString: String?
var newDueString: String?
var newTimeString: String?
var setFlagged: Bool? 
var newCalendarIdentifier: String? 

// Arg parsing
var args = CommandLine.arguments
args.removeFirst()

while !args.isEmpty {
    let arg = args.removeFirst()
    switch arg {
    case "--id":
        guard !args.isEmpty else { logError("Missing value for --id"); exit(1) }
        searchId = args.removeFirst()
    case "--title": // Search by title
        guard !args.isEmpty else { logError("Missing value for --title"); exit(1) }
        searchTitle = args.removeFirst()
    
    // Updates
    case "--new-title":
        guard !args.isEmpty else { logError("Missing value for --new-title"); exit(1) }
        newTitle = args.removeFirst()
    case "--notes":
        guard !args.isEmpty else { logError("Missing value for --notes"); exit(1) }
        newNotes = args.removeFirst()
    case "--priority":
        guard !args.isEmpty else { logError("Missing value for --priority"); exit(1) }
        newPriority = Int(args.removeFirst())
    case "--url":
        guard !args.isEmpty else { logError("Missing value for --url"); exit(1) }
        newUrlString = args.removeFirst()
    case "--due":
        guard !args.isEmpty else { logError("Missing value for --due"); exit(1) }
        newDueString = args.removeFirst()
    case "--time":
        guard !args.isEmpty else { logError("Missing value for --time"); exit(1) }
        newTimeString = args.removeFirst()
    case "--flagged", "-f":
        setFlagged = true
    case "--unflagged":
        setFlagged = false
    case "--move-to-list":
        guard !args.isEmpty else { logError("Missing value for --move-to-list"); exit(1) }
        newCalendarIdentifier = args.removeFirst()
    default:
        // Assume positional arg is title if not id provided?
        // Let's stick to flags for clarity, or if searchTitle empty, assume it matches title.
        if searchTitle == nil && searchId == nil {
            searchTitle = arg
        }
    }
}

if searchId == nil && searchTitle == nil {
    logError("Must specify task via --id or Provide a title argument")
    exit(1)
}

let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)

// Function to calculate due date (reused logic)
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
    } else { // YYYY-MM-DD
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        date = formatter.date(from: dateStr)
    }
    
    guard let resolvedDate = date else { return nil }
    var components = Calendar.current.dateComponents([.year, .month, .day], from: resolvedDate)
    
    if let t = timeStr {
        let parts = t.components(separatedBy: ":")
        if parts.count == 2, let h = Int(parts[0]), let m = Int(parts[1]) {
            components.hour = h
            components.minute = m
        }
    }
    return components
}

func updateFlagged(reminderId: String, state: Bool) {
    let boolStr = state ? "true" : "false"
    // AppleScript shim
    let script = """
    tell application "Reminders"
        try
            set targetTask to (first reminder whose id is "x-apple-reminder://\(reminderId)")
            set flagged of targetTask to \(boolStr)
        on error
            try
                set targetTask to (first reminder whose id is "\(reminderId)")
                set flagged of targetTask to \(boolStr)
            end try
        end try
    end tell
    """
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
    process.arguments = ["-e", script]
    try? process.run()
    process.waitUntilExit()
}

func performEdit() {
    var reminder: EKReminder?
    
    if let id = searchId {
        reminder = store.calendarItem(withIdentifier: id) as? EKReminder
    } else if let title = searchTitle {
        // Search by title (inefficient, needs fetch)
        let calendars = store.calendars(for: .reminder)
        let predicate = store.predicateForReminders(in: calendars)
        // We have to wait for fetch
        store.fetchReminders(matching: predicate) { reminders in
            if let reminders = reminders {
                // Approximate match? or Exact?
                // Let's do exact match first
                reminder = reminders.first(where: { 
                    $0.title.caseInsensitiveCompare(title) == .orderedSame && !$0.isCompleted 
                })
            }
            // Proceed to update if found
            if let r = reminder {
                applyUpdates(to: r)
            } else {
                logError("Task not found with title '\(title)'")
                semaphore.signal()
                exit(1)
            }
        }
        return // async flow
    }
    
    if let r = reminder {
        applyUpdates(to: r)
    } else {
        if let id = searchId { logError("Task not found with ID '\(id)'") }
        exit(1)
    }
}

func applyUpdates(to reminder: EKReminder) {
    // Apply changes
    var changed = false
    
    if let t = newTitle { reminder.title = t; changed = true }
    if let n = newNotes { reminder.notes = n; changed = true }
    if let p = newPriority { reminder.priority = p; changed = true }
    
    if let uStr = newUrlString {
        if let u = URL(string: uStr) {
            reminder.url = u
            changed = true
        }
    }

    if let calId = newCalendarIdentifier {
        let calendars = store.calendars(for: .reminder)
        var target: EKCalendar? = calendars.first { $0.calendarIdentifier == calId }
        
        if target == nil {
             target = calendars.first { $0.title == calId }
        }
        
        if let t = target {
            reminder.calendar = t
            changed = true
        } else {
            logError("Target list not found: \(calId)")
            exit(1)
        }
    }
    
    // Date update
    // If only time provided, need existing date? 
    // Logic: if newDue provided, use it. If only newTime provided, use existing due date + new time.
    if let dStr = newDueString {
        if let comps = calculateDueDate(dateStr: dStr, timeStr: newTimeString) {
            reminder.dueDateComponents = comps
            changed = true
        }
    } else if let tStr = newTimeString {
        // Only time updated
        if var current = reminder.dueDateComponents {
            // Update time parts
             let parts = tStr.components(separatedBy: ":")
             if parts.count == 2, let h = Int(parts[0]), let m = Int(parts[1]) {
                current.hour = h
                current.minute = m
                reminder.dueDateComponents = current
                changed = true
             }
        } else {
            // No due date exists, cannot set time only (assume today?)
            // Let's assume today
            if let comps = calculateDueDate(dateStr: "today", timeStr: tStr) {
                 reminder.dueDateComponents = comps
                 changed = true
            }
        }
    }
    
    // Save
    do {
        if changed {
             try store.save(reminder, commit: true)
        }
        
        // Flagged is separate
        if let f = setFlagged {
            updateFlagged(reminderId: reminder.calendarItemIdentifier, state: f)
        }
        
        logSuccess("✅ Updated task")
        semaphore.signal()
    } catch {
        logError("Failed to update: \(error)")
        exit(1)
    }
}

if #available(macOS 14.0, *) {
    store.requestFullAccessToReminders { (granted, error) in
        if granted { performEdit() }
        else { exit(1) }
    }
} else {
    store.requestAccess(to: .reminder) { (granted, error) in
        if granted { performEdit() }
        else { exit(1) }
    }
}

semaphore.wait()
