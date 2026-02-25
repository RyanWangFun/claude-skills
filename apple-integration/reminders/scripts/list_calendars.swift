#!/usr/bin/env swift

import Foundation
import EventKit

// Define a struct to mirror the desired JSON output
struct CalendarInfo: Codable {
    let id: String
    let title: String
    let color: String? // Hex string if available
    let source: String
    let type: String
    let allowsContentModifications: Bool
}

// Helper to convert CGColor to Hex String (Basic implementation)
func hexString(from cgColor: CGColor?) -> String? {
    guard let cgColor = cgColor else { return nil }
    guard let components = cgColor.components else { return nil }
    let count = cgColor.numberOfComponents
    
    var r: CGFloat = 0
    var g: CGFloat = 0
    var b: CGFloat = 0
    
    if count >= 3 {
        r = components[0]
        g = components[1]
        b = components[2]
    } else if count == 2 {
        // Grayscale with alpha?
        r = components[0]
        g = components[0]
        b = components[0]
    } else {
        return nil
    }

    return String(format: "#%02lX%02lX%02lX", lroundf(Float(r * 255)), lroundf(Float(g * 255)), lroundf(Float(b * 255)))
}

let store = EKEventStore()

// Use a semaphore to wait for the async requestAccess to complete
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

// Get all calendars capable of storing reminders
let calendars = store.calendars(for: .reminder)

var result: [CalendarInfo] = []

for calendar in calendars {
    let info = CalendarInfo(
        id: calendar.calendarIdentifier,
        title: calendar.title,
        color: hexString(from: calendar.cgColor),
        source: calendar.source.title,
        type: String(describing: calendar.type), // e.g., local, calDAV, etc.
        allowsContentModifications: calendar.allowsContentModifications
    )
    result.append(info)
}

let encoder = JSONEncoder()
encoder.outputFormatting = .prettyPrinted

do {
    let jsonData = try encoder.encode(result)
    if let jsonString = String(data: jsonData, encoding: .utf8) {
        print(jsonString)
    }
} catch {
    print("Error encoding JSON: \(error)")
    exit(1)
}
