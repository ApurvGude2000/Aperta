import Foundation

/// Manages local storage of events and recordings
class EventStorageManager {
    static let shared = EventStorageManager()

    private init() {
        createEventsDirectoryIfNeeded()
    }

    // MARK: - Directory Setup

    /// Get the base events directoryshttp
    private var eventsDirectory: URL {
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return documentsPath.appendingPathComponent("events")
    }

    /// Create events directory if it doesn't exist
    private func createEventsDirectoryIfNeeded() {
        let fileManager = FileManager.default
        if !fileManager.fileExists(atPath: eventsDirectory.path) {
            try? fileManager.createDirectory(at: eventsDirectory, withIntermediateDirectories: true)
            print("📁 Created events directory at: \(eventsDirectory.path)")
        }
    }

    // MARK: - Event Management

    /// Save an event to local storage
    func saveEvent(_ event: Event) throws {
        let eventFolder = eventsDirectory.appendingPathComponent(event.id.uuidString)
        let fileManager = FileManager.default

        // Create event folder
        if !fileManager.fileExists(atPath: eventFolder.path) {
            try fileManager.createDirectory(at: eventFolder, withIntermediateDirectories: true)
            print("📁 Created event folder: \(event.name)")
        }

        // Save event.json
        let eventFile = eventFolder.appendingPathComponent("event.json")
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = .prettyPrinted
        let data = try encoder.encode(event)
        try data.write(to: eventFile)

        print("✅ Saved event: \(event.name) to \(eventFile.path)")
    }

    /// Load all events from local storage
    func loadAllEvents() throws -> [Event] {
        let fileManager = FileManager.default

        guard fileManager.fileExists(atPath: eventsDirectory.path) else {
            print("📁 No events directory found, returning empty array")
            return []
        }

        let eventFolders = try fileManager.contentsOfDirectory(
            at: eventsDirectory,
            includingPropertiesForKeys: nil
        )

        var events: [Event] = []
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        for folder in eventFolders {
            let eventFile = folder.appendingPathComponent("event.json")

            if fileManager.fileExists(atPath: eventFile.path) {
                do {
                    let data = try Data(contentsOf: eventFile)
                    let event = try decoder.decode(Event.self, from: data)
                    events.append(event)
                } catch {
                    print("⚠️ Failed to load event from \(eventFile.path): \(error)")
                }
            }
        }

        print("📂 Loaded \(events.count) events from storage")
        return events.sorted { $0.date > $1.date } // Most recent first
    }

    /// Delete an event from local storage
    func deleteEvent(_ event: Event) throws {
        let eventFolder = eventsDirectory.appendingPathComponent(event.id.uuidString)
        try FileManager.default.removeItem(at: eventFolder)
        print("🗑️ Deleted event: \(event.name)")
    }

    // MARK: - Recording Management (for later)

    /// Get recordings folder for an event
    func recordingsFolder(for event: Event) -> URL {
        let eventFolder = eventsDirectory.appendingPathComponent(event.id.uuidString)
        return eventFolder.appendingPathComponent("recordings")
    }

    /// Create recordings folder if needed
    func createRecordingsFolderIfNeeded(for event: Event) throws {
        let folder = recordingsFolder(for: event)
        let fileManager = FileManager.default

        if !fileManager.fileExists(atPath: folder.path) {
            try fileManager.createDirectory(at: folder, withIntermediateDirectories: true)
            print("📁 Created recordings folder for: \(event.name)")
        }
    }
}
