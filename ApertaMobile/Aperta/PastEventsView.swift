import SwiftUI

struct PastEventsView: View {
    @State private var events: [Event] = []
    @State private var eventToDelete: Event?
    @State private var showDeleteConfirmation = false

    var body: some View {
        List {
            if events.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "calendar.badge.clock")
                        .font(.system(size: 60))
                        .foregroundColor(.gray)
                    Text("No past events yet")
                        .font(.headline)
                        .foregroundColor(.gray)
                    Text("Your recorded events will appear here")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity)
                .padding(.top, 100)
                .listRowBackground(Color.clear)
            } else {
                ForEach(events) { event in
                    NavigationLink(destination: EventDetailView(event: event)) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(event.name)
                                .font(.headline)
                            HStack {
                                Image(systemName: "location.fill")
                                    .font(.caption)
                                Text(event.location)
                                    .font(.subheadline)
                                    .foregroundColor(.gray)
                            }
                            Text(event.date, style: .date)
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        .padding(.vertical, 4)
                    }
                    .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                        Button(role: .destructive) {
                            eventToDelete = event
                            showDeleteConfirmation = true
                        } label: {
                            Label("Delete", systemImage: "trash")
                        }
                    }
                }
            }
        }
        .navigationTitle("Past Events")
        .onAppear {
            loadEvents()
        }
        .confirmationDialog(
            "Delete Event",
            isPresented: $showDeleteConfirmation,
            presenting: eventToDelete
        ) { event in
            Button("Delete", role: .destructive) {
                deleteEvent(event)
            }
            Button("Cancel", role: .cancel) {}
        } message: { event in
            Text("Are you sure you want to delete '\(event.name)'? This action cannot be undone.")
        }
    }

    private func deleteEvent(_ event: Event) {
        do {
            try EventStorageManager.shared.deleteEvent(event)
            events.removeAll { $0.id == event.id }
            print("✅ Deleted event: \(event.name)")
        } catch {
            print("❌ Failed to delete event: \(error)")
        }
    }

    private func loadEvents() {
        do {
            events = try EventStorageManager.shared.loadAllEvents()
            print("✅ Loaded \(events.count) events")
        } catch {
            print("❌ Failed to load events: \(error)")
        }
    }
}

struct EventDetailView: View {
    let event: Event
    
    var body: some View {
        List {
            Section("Event Details") {
                LabeledContent("Name", value: event.name)
                LabeledContent("Location", value: event.location)
                LabeledContent("Date", value: event.date, format: .dateTime)
            }
            
            Section("Recordings") {
                if event.recordings.isEmpty {
                    Text("No recordings yet")
                        .foregroundColor(.gray)
                } else {
                    ForEach(event.recordings) { recording in
                        NavigationLink(destination: TranscriptDetailView(recording: recording)) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Recording \(recording.startTime, style: .time)")
                                    .font(.headline)
                                if let duration = recording.duration {
                                    Text("Duration: \(Int(duration))s")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                            }
                        }
                    }
                }
            }
        }
        .navigationTitle(event.name)
    }
}

struct TranscriptDetailView: View {
    let recording: Recording
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Recording info
                VStack(alignment: .leading, spacing: 8) {
                    Text("Started: \(recording.startTime, style: .time)")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    if let endTime = recording.endTime {
                        Text("Ended: \(endTime, style: .time)")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    if let duration = recording.duration {
                        Text("Duration: \(formatDuration(duration))")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                }
                .padding()
                
                Divider()
                
                // Transcript with timestamps
                VStack(alignment: .leading, spacing: 12) {
                    Text("Transcript")
                        .font(.headline)
                        .padding(.horizontal)
                    
                    if recording.segments.isEmpty {
                        Text(recording.transcript)
                            .padding()
                    } else {
                        ForEach(recording.segments) { segment in
                            HStack(alignment: .top, spacing: 12) {
                                Text(formatTimestamp(segment.startTime))
                                    .font(.caption)
                                    .foregroundColor(.blue)
                                    .frame(width: 60, alignment: .leading)
                                
                                Text(segment.text)
                                    .font(.body)
                                
                                Spacer()
                            }
                            .padding(.horizontal)
                        }
                    }
                }
            }
        }
        .navigationTitle("Transcript")
    }
    
    private func formatTimestamp(_ seconds: Double) -> String {
        let minutes = Int(seconds) / 60
        let secs = Int(seconds) % 60
        return String(format: "%d:%02d", minutes, secs)
    }
    
    private func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        return "\(minutes)m \(seconds)s"
    }
}

#Preview {
    NavigationStack {
        PastEventsView()
    }
}
