import EventKit
import Foundation

let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)

func fetchLists() {
    let calendars = store.calendars(for: .reminder)
    for calendar in calendars {
        print(calendar.title)
    }
}

if #available(macOS 14.0, *) {
    store.requestFullAccessToReminders { (granted, error) in
        if granted {
            fetchLists()
        } else {
            // Ideally output to stderr
            fputs("Access denied or error: \(String(describing: error))\n", stderr)
            exit(1)
        }
        semaphore.signal()
    }
} else {
    store.requestAccess(to: .reminder) { (granted, error) in
        if granted {
            fetchLists()
        } else {
            fputs("Access denied or error: \(String(describing: error))\n", stderr)
            exit(1)
        }
        semaphore.signal()
    }
}

semaphore.wait()
