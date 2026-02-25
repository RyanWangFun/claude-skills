#!/usr/bin/env swift

import Foundation
import EventKit

// Arguments: <id-or-title> [--execute]
let args = CommandLine.arguments

guard args.count >= 2 else {
    print("Usage: delete_calendar <id-or-title> [--execute]")
    exit(1)
}

let identifier = args[1]
let execute = args.contains("--execute")

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
var targetCalendar: EKCalendar?

// 1. Exact ID
targetCalendar = calendars.first { $0.calendarIdentifier == identifier }
// 2. Suffix ID
if targetCalendar == nil && identifier.count >= 4 {
     targetCalendar = calendars.first { $0.calendarIdentifier.hasSuffix(identifier) }
}
// 3. Exact Title
if targetCalendar == nil {
    targetCalendar = calendars.first { $0.title == identifier }
}

guard let calendar = targetCalendar else {
    print("Error: List not found: \(identifier)")
    exit(1)
}

// Check for tasks
let predicate = store.predicateForReminders(in: [calendar])
let countSema = DispatchSemaphore(value: 0)
var taskCount = 0

store.fetchReminders(matching: predicate) { reminders in
    taskCount = reminders?.count ?? 0
    countSema.signal()
}
countSema.wait()

if !execute {
    // Just return info
    print("List: \(calendar.title)")
    print("ID: \(calendar.calendarIdentifier)")
    print("Tasks: \(taskCount)")
    // Use a special exit code or output format if needed, but plain text is fine for CLI parsing
    exit(0)
}

// Execute deletion
do {
    try store.removeCalendar(calendar, commit: true)
    print("Successfully deleted list: \(calendar.title)")
} catch {
    print("Error deleting list: \(error.localizedDescription)")
    exit(1)
}
