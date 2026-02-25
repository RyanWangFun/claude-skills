import EventKit
import Foundation

func logError(_ message: String) {
    fputs("❌ Error: \(message)\n", stderr)
}

func logSuccess(_ message: String) {
    print(message)
}

var taskName: String?

// Args parsing
var args = CommandLine.arguments
args.removeFirst()

if !args.isEmpty {
    taskName = args.removeFirst()
}

guard let title = taskName else {
    logError("Task name required")
    exit(1)
}

let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)

func performComplete() {
    let calendars = store.calendars(for: .reminder)
    let predicate = store.predicateForReminders(in: calendars)
    
    store.fetchReminders(matching: predicate) { reminders in
        guard let reminders = reminders else {
            semaphore.signal()
            return
        }
        
        // Find *incomplete* reminder with matching title
        // Note: AppleScript logic stopped at first match `foundList`, `exit repeat`.
        // We should replicate that behavior (complete first match).
        
        if let target = reminders.first(where: { $0.title == title && !$0.isCompleted }) {
            target.isCompleted = true
            do {
                try store.save(target, commit: true)
                logSuccess("✅ Marked task '\(title)' as completed in list '\(target.calendar.title)'")
            } catch {
                logError("Failed to save reminder: \(error.localizedDescription)")
                exit(1)
            }
        } else {
             // Check if it exists but already completed? 
             // AppleScript version just said "NOT_FOUND" for both cases (missing or completed).
             // Let's stick to "Task not found or already completed"
             logError("Task '\(title)' not found or already completed")
             // Using logError here but exiting 0 or 1? 
             // cmd_done.sh treats "NOT_FOUND" as a warning but exit 0?
             // Actually cmd_done.sh exits 0 if result is "NOT_FOUND" string (via osascript return) 
             // but then prints "⚠️  Task ... not found".
             // Here we are native. Let's print the warning to stdout or stderr and exit 0 or 1.
             // If I exit 1, cmd_done.sh might think critical failure.
             // If I exit 0 and print to stderr, it's fine.
             // Let's print the specific warning message expected via stdout?
             // Actually cmd_done.sh will be replaced to just call this. 
             // So this script defines the output. 
             // I'll make it exit 1 so the wrapper knows it failed to find it, 
             // BUT `cmd_done.sh` logic was "if NOT_FOUND then print warning else print success".
             // Meaning it wasn't a hard error in the sense of script crash.
             // Let's exit 1 for "not found" so the caller knows.
             exit(1)
        }
        semaphore.signal()
    }
}

if #available(macOS 14.0, *) {
    store.requestFullAccessToReminders { (granted, error) in
        if granted {
            performComplete()
        } else {
            logError("Access denied: \(String(describing: error))")
            exit(1)
        }
    }
} else {
    store.requestAccess(to: .reminder) { (granted, error) in
        if granted {
            performComplete()
        } else {
            logError("Access denied: \(String(describing: error))")
            exit(1)
        }
    }
}

semaphore.wait()
