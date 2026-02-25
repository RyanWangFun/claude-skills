import EventKit
import Foundation

func logError(_ message: String) {
    fputs("❌ Error: \(message)\n", stderr)
}
func logSuccess(_ message: String) {
    print(message)
}

var searchId: String?
var searchTitle: String?

var args = CommandLine.arguments
args.removeFirst()

while !args.isEmpty {
    let arg = args.removeFirst()
    switch arg {
    case "--id":
        if !args.isEmpty { searchId = args.removeFirst() }
    case "--title":
        if !args.isEmpty { searchTitle = args.removeFirst() }
    default:
        if searchId == nil && searchTitle == nil {
            searchTitle = arg
        }
    }
}

if searchId == nil && searchTitle == nil {
    logError("Provide ID via --id or Title")
    exit(1)
}

let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)

func performDelete() {
    if let id = searchId {
        if let reminder = store.calendarItem(withIdentifier: id) as? EKReminder {
            delete(reminder)
        } else {
            logError("Task not found with ID '\(id)'")
            exit(1)
        }
    } else if let title = searchTitle {
        let calendars = store.calendars(for: .reminder)
        let predicate = store.predicateForReminders(in: calendars)
        store.fetchReminders(matching: predicate) { reminders in
            if let target = reminders?.first(where: { 
                $0.title.caseInsensitiveCompare(title) == .orderedSame && !$0.isCompleted 
            }) {
                delete(target)
            } else {
                logError("Task not found with title '\(title)'")
                semaphore.signal()
                exit(1)
            }
        }
    }
}

func delete(_ reminder: EKReminder) {
    do {
        let title = reminder.title ?? "Unknown"
        try store.remove(reminder, commit: true)
        logSuccess("🗑️ Deleted task '\(title)'")
        semaphore.signal()
    } catch {
        logError("Failed to delete: \(error)")
        exit(1)
    }
}

if #available(macOS 14.0, *) {
    store.requestFullAccessToReminders { (granted, error) in
        if granted { performDelete() } else { exit(1) }
    }
} else {
    store.requestAccess(to: .reminder) { (granted, error) in
        if granted { performDelete() } else { exit(1) }
    }
}

semaphore.wait()
