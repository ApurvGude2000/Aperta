import Foundation

/// Represents a conference event with recordings
struct Event: Identifiable, Codable {
    let id: UUID
    var name: String
    var location: String
    var date: Date
    var recordings: [Recording]
    var isActive: Bool
    
    init(id: UUID = UUID(), name: String, location: String, date: Date = Date()) {
        self.id = id
        self.name = name
        self.location = location
        self.date = date
        self.recordings = []
        self.isActive = true
    }
}

/// Represents a single recording within an event
struct Recording: Identifiable, Codable {
    let id: UUID
    var transcript: String
    var segments: [TranscriptSegment]
    var startTime: Date
    var endTime: Date?
    
    init(id: UUID = UUID(), transcript: String = "", segments: [TranscriptSegment] = [], startTime: Date = Date()) {
        self.id = id
        self.transcript = transcript
        self.segments = segments
        self.startTime = startTime
        self.endTime = nil
    }
    
    var duration: TimeInterval? {
        guard let endTime else { return nil }
        return endTime.timeIntervalSince(startTime)
    }
}

/// Represents a transcript segment with timestamp
struct TranscriptSegment: Identifiable, Codable {
    let id: UUID
    let text: String
    let startTime: Double
    let endTime: Double
    
    init(id: UUID = UUID(), text: String, startTime: Double, endTime: Double) {
        self.id = id
        self.text = text
        self.startTime = startTime
        self.endTime = endTime
    }
}
