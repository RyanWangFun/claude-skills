#!/usr/bin/env swift

import Foundation
import EventKit

// Arguments: <id-or-title> <new-title>
let args = CommandLine.arguments

guard args.count == 3 else {
    print("Usage: rename_calendar <id-or-title> <new-title>")
    exit(1)
}

let identifier = args[1]
let newTitle = args[2]

let store = EKEventStore()
let sema = DispatchSemaphore(value: 0)

store.requestAccess(to: .reminder) { (granted, error) in
    if !granted {
        print("Access denied")
        sema.signal()
        exit(1)
    }
    sema.signal()
}
sema.wait()

let calendars = store.calendars(for: .reminder)

// Find calendar by ID (prefix check supported for convenience in CLI) or Title
var targetCalendar: EKCalendar?

// 1. Try exact ID match
targetCalendar = calendars.first { $0.calendarIdentifier == identifier }

// 2. Try ID suffix match (last 8 chars) if identifier is short
if targetCalendar == nil && identifier.count >= 4 {
     targetCalendar = calendars.first { $0.calendarIdentifier.hasSuffix(identifier) }
}

// 3. Try Exact Title match
if targetCalendar == nil {
    targetCalendar = calendars.first { $0.title == identifier }
}

guard let calendar = targetCalendar else {
    print("Error: List not found with identifier or title: \(identifier)")
    exit(1)
}

if !calendar.allowsContentModifications {
    print("Error: List '\(calendar.title)' is not modifiable.")
    exit(1)
}

let oldTitle = calendar.title
calendar.title = newTitle

do {
    try store.saveCalendar(calendar, commit: true)
    print("Successfully renamed list from '\(oldTitle)' to '\(newTitle)'")
} catch {
    print("Error renaming list: \(error.localizedDescription)")
    exit(1)
}
