#!/usr/bin/env swift

import Foundation
import EventKit

// Arguments: <title> [color-hex]
let args = CommandLine.arguments

guard args.count >= 2 else {
    print("Usage: create_calendar <title> [color-hex]")
    exit(1)
}

let title = args[1]
let colorHex = args.count > 2 ? args[2] : nil

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

// Helper to convert Hex to CGColor
func color(from hex: String) -> CGColor? {
    var hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
    hexSanitized = hexSanitized.replacingOccurrences(of: "#", with: "")

    var rgb: UInt64 = 0

    guard Scanner(string: hexSanitized).scanHexInt64(&rgb) else { return nil }

    let length = hexSanitized.count
    let r, g, b: CGFloat

    if length == 6 {
        r = CGFloat((rgb & 0xFF0000) >> 16) / 255.0
        g = CGFloat((rgb & 0x00FF00) >> 8) / 255.0
        b = CGFloat(rgb & 0x0000FF) / 255.0
        return CGColor(srgbRed: r, green: g, blue: b, alpha: 1.0)
    }
    return nil
}

// Find best source (prioritize iCloud/CalDAV, fallback to Local)
let sources = store.sources
var bestSource: EKSource?

// Priority 1: CalDAV (usually iCloud)
bestSource = sources.first { $0.sourceType == .calDAV && $0.title == "iCloud" }

// Priority 2: Any CalDAV
if bestSource == nil {
    bestSource = sources.first { $0.sourceType == .calDAV }
}

// Priority 3: Local
if bestSource == nil {
    bestSource = sources.first { $0.sourceType == .local }
}

guard let source = bestSource else {
    print("Error: No suitable source found to create calendar.")
    exit(1)
}

// Create Calendar
let newCalendar = EKCalendar(for: .reminder, eventStore: store)
newCalendar.title = title
newCalendar.source = source

if let hex = colorHex, let cgColor = color(from: hex) {
    newCalendar.cgColor = cgColor
}

do {
    try store.saveCalendar(newCalendar, commit: true)
    print("Successfully created list: \(newCalendar.title)")
    print("ID: \(newCalendar.calendarIdentifier)")
} catch {
    print("Error creating list: \(error.localizedDescription)")
    exit(1)
}
